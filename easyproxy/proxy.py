"""简单的HTTP/HTTPS/SOCKS5代理服务器实现"""

import asyncio
import struct
import time
from typing import Tuple, Optional
from urllib.parse import urlparse

from .config import ProxyConfig
from .logger import get_logger, AccessLogger, ConnectionStats
from .auth import create_authenticator, Authenticator

logger = get_logger(__name__)


class SimpleHTTPProxy:
    """简单的HTTP/HTTPS/SOCKS5代理服务器"""
    
    def __init__(self, config: Optional[ProxyConfig] = None):
        """
        初始化代理服务器
        
        Args:
            config: 配置对象,如果为None则使用默认配置
        """
        self.config = config or ProxyConfig()
        self.server = None
        
        # 配置日志
        self._setup_logging()
        
        # 访问日志和统计
        self.access_logger = AccessLogger(enabled=self.config.access_log)
        self.stats = ConnectionStats()
        
        # 认证器
        self.authenticator = create_authenticator(self.config.auth)
    
    def _setup_logging(self) -> None:
        """配置日志系统"""
        from .logger import setup_logging
        
        setup_logging(
            log_level=self.config.log_level,
            log_file=self.config.log_file,
            json_format=False  # 可以根据配置决定
        )
        
    async def handle_client(
        self, 
        client_reader: asyncio.StreamReader, 
        client_writer: asyncio.StreamWriter
    ) -> None:
        """处理客户端连接"""
        client_addr = client_writer.get_extra_info('peername')
        client_ip, client_port = client_addr if client_addr else ("unknown", 0)
        start_time = time.time()
        
        protocol = "unknown"
        target_host = "unknown"
        target_port = 0
        bytes_sent = 0
        bytes_received = 0
        error_msg = None
        
        logger.info("new_connection", client=f"{client_ip}:{client_port}")
        
        try:
            # 读取第一个字节来检测协议
            first_byte = await client_reader.read(1)
            if not first_byte:
                return
            
            # 检测SOCKS5协议 (第一个字节是0x05)
            if first_byte[0] == 0x05:
                protocol = "socks5"
                self.stats.increment_connection(protocol)
                logger.info("protocol_detected", protocol=protocol, client=f"{client_ip}:{client_port}")
                
                result = await self._handle_socks5(
                    first_byte, client_reader, client_writer,
                    client_ip, client_port
                )
                if result:
                    target_host, target_port, bytes_sent, bytes_received = result
                return
            
            # 否则按HTTP/HTTPS处理
            # 读取完整的请求行
            rest_of_line = await client_reader.readline()
            request_line = (first_byte + rest_of_line).decode('utf-8', errors='ignore')
            logger.debug("http_request_line", request=request_line.strip())
            
            # 解析请求
            parts = request_line.split()
            if len(parts) < 3:
                logger.warning("无效的HTTP请求")
                return
                
            method, url, version = parts[0], parts[1], parts[2]
            
            # 读取所有请求头
            headers = []
            auth_header = None
            while True:
                line = await client_reader.readline()
                if not line or line == b'\r\n':
                    break
                headers.append(line)
                
                # 提取Proxy-Authorization头
                header_str = line.decode('utf-8', errors='ignore')
                if header_str.lower().startswith('proxy-authorization:'):
                    auth_header = header_str.split(':', 1)[1].strip()
            
            # HTTP/HTTPS认证检查
            if self.authenticator.is_enabled():
                auth_success, username = self.authenticator.authenticate_http(auth_header)
                if not auth_success:
                    logger.warning("http_auth_failed", client=f"{client_ip}:{client_port}")
                    # 返回407 Proxy Authentication Required
                    response = self.authenticator.generate_http_401_response()
                    client_writer.write(response)
                    await client_writer.drain()
                    return
                logger.info("http_auth_success", username=username, client=f"{client_ip}:{client_port}")
            
            # 检查是否是CONNECT方法(HTTPS隧道)
            if method.upper() == "CONNECT":
                protocol = "https"
                self.stats.increment_connection(protocol)
                
                result = await self._handle_connect(
                    url, client_reader, client_writer,
                    client_ip, client_port
                )
                if result:
                    target_host, target_port, bytes_sent, bytes_received = result
                return
            
            # 处理普通HTTP请求
            protocol = "http"
            self.stats.increment_connection(protocol)
            
            # 解析目标地址
            target_host, target_port = self._parse_target(url)
            if not target_host:
                error_msg = f"无法解析目标地址: {url}"
                logger.error("parse_target_failed", url=url)
                return
            
            logger.info("connecting_to_target", target=f"{target_host}:{target_port}")
            
            # 连接到目标服务器
            try:
                target_reader, target_writer = await asyncio.wait_for(
                    asyncio.open_connection(target_host, target_port),
                    timeout=self.config.connection_timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"连接超时: {target_host}:{target_port}")
                return
            except Exception as e:
                logger.error(f"连接失败: {target_host}:{target_port} - {e}")
                return
            
            # 构建并发送请求到目标服务器
            # 对于HTTP代理,需要修改请求行为相对路径
            parsed = urlparse(url)
            path = parsed.path or "/"
            if parsed.query:
                path += f"?{parsed.query}"
            
            # 重建请求
            target_request = f"{method} {path} {version}\r\n".encode()
            target_writer.write(target_request)
            
            # 转发请求头(过滤代理相关头)
            for header in headers:
                header_str = header.decode('utf-8', errors='ignore').lower()
                if not header_str.startswith('proxy-'):
                    target_writer.write(header)
            
            target_writer.write(b'\r\n')
            await target_writer.drain()
            
            # 双向转发数据
            await self._forward_data(client_reader, client_writer, 
                                    target_reader, target_writer)
            
        except Exception as e:
            error_msg = str(e)
            self.stats.increment_error()
            logger.error("connection_error", error=error_msg, exc_info=True)
        finally:
            # 计算连接时长
            duration_ms = (time.time() - start_time) * 1000
            
            # 更新统计
            self.stats.decrement_connection()
            if bytes_sent > 0 or bytes_received > 0:
                self.stats.add_traffic(bytes_sent, bytes_received)
            
            # 记录访问日志
            self.access_logger.log_request(
                client_ip=client_ip,
                client_port=client_port,
                protocol=protocol,
                target_host=target_host,
                target_port=target_port,
                status="error" if error_msg else "success",
                bytes_sent=bytes_sent,
                bytes_received=bytes_received,
                duration_ms=duration_ms,
                error=error_msg
            )
            
            # 关闭连接
            try:
                client_writer.close()
                await client_writer.wait_closed()
            except:
                pass
            
            logger.debug("connection_closed", 
                        client=f"{client_ip}:{client_port}",
                        duration_ms=round(duration_ms, 2))
    
    async def _handle_connect(
        self,
        target: str,
        client_reader: asyncio.StreamReader,
        client_writer: asyncio.StreamWriter,
        client_ip: str,
        client_port: int
    ) -> Optional[Tuple[str, int, int, int]]:
        """
        处理HTTPS CONNECT隧道
        
        Returns:
            Optional[Tuple[str, int, int, int]]: (target_host, target_port, bytes_sent, bytes_received) 或 None
        """
        try:
            # 解析目标地址 (格式: host:port)
            if ':' in target:
                host, port_str = target.rsplit(':', 1)
                port = int(port_str)
            else:
                host = target
                port = 443
            
            logger.info("connect_tunnel", target=f"{host}:{port}", client=f"{client_ip}:{client_port}")
            
            # 连接到目标服务器
            try:
                target_reader, target_writer = await asyncio.wait_for(
                    asyncio.open_connection(host, port),
                    timeout=self.config.connection_timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"CONNECT连接超时: {host}:{port}")
                client_writer.write(b"HTTP/1.1 504 Gateway Timeout\r\n\r\n")
                await client_writer.drain()
                return
            except Exception as e:
                logger.error(f"CONNECT连接失败: {host}:{port} - {e}")
                client_writer.write(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                await client_writer.drain()
                return
            
            # 返回连接成功响应
            client_writer.write(b"HTTP/1.1 200 Connection Established\r\n\r\n")
            await client_writer.drain()
            
            logger.info("connect_tunnel_established", target=f"{host}:{port}")
            
            # 进入透明转发模式(不解密TLS)
            bytes_sent, bytes_received = await self._forward_data_with_stats(
                client_reader, client_writer,
                target_reader, target_writer
            )
            
            return (host, port, bytes_sent, bytes_received)
            
        except Exception as e:
            logger.error("connect_error", error=str(e), exc_info=True)
            return None
    
    def _parse_target(self, url: str) -> Tuple[str, int]:
        """解析目标地址和端口"""
        try:
            # HTTP代理请求通常是完整URL
            if url.startswith('http://'):
                parsed = urlparse(url)
                host = parsed.hostname
                port = parsed.port or 80
                return host, port
            else:
                # 可能是相对路径,这种情况下无法处理
                return None, None
        except Exception as e:
            logger.error(f"解析URL失败: {url} - {e}")
            return None, None
    
    async def _forward_data(
        self,
        client_reader: asyncio.StreamReader,
        client_writer: asyncio.StreamWriter,
        target_reader: asyncio.StreamReader,
        target_writer: asyncio.StreamWriter
    ) -> None:
        """双向转发数据(无统计)"""
        async def forward(reader, writer, direction):
            try:
                while True:
                    data = await reader.read(self.config.buffer_size)
                    if not data:
                        break
                    writer.write(data)
                    await writer.drain()
            except Exception as e:
                logger.debug("forward_error", direction=direction, error=str(e))
            finally:
                try:
                    writer.close()
                    await writer.wait_closed()
                except:
                    pass
        
        # 并发执行双向转发
        await asyncio.gather(
            forward(target_reader, client_writer, "target->client"),
            forward(client_reader, target_writer, "client->target"),
            return_exceptions=True
        )
    
    async def _forward_data_with_stats(
        self,
        client_reader: asyncio.StreamReader,
        client_writer: asyncio.StreamWriter,
        target_reader: asyncio.StreamReader,
        target_writer: asyncio.StreamWriter
    ) -> Tuple[int, int]:
        """
        双向转发数据并统计流量
        
        Returns:
            Tuple[int, int]: (bytes_sent, bytes_received)
        """
        bytes_to_client = 0
        bytes_to_target = 0
        
        async def forward(reader, writer, direction):
            nonlocal bytes_to_client, bytes_to_target
            try:
                while True:
                    data = await reader.read(self.config.buffer_size)
                    if not data:
                        break
                    writer.write(data)
                    await writer.drain()
                    
                    # 统计流量
                    if direction == "target->client":
                        bytes_to_client += len(data)
                    else:
                        bytes_to_target += len(data)
            except Exception as e:
                logger.debug("forward_error", direction=direction, error=str(e))
            finally:
                try:
                    writer.close()
                    await writer.wait_closed()
                except:
                    pass
        
        # 并发执行双向转发
        await asyncio.gather(
            forward(target_reader, client_writer, "target->client"),
            forward(client_reader, target_writer, "client->target"),
            return_exceptions=True
        )
        
        return (bytes_to_target, bytes_to_client)
    
    async def _handle_socks5(
        self,
        first_byte: bytes,
        client_reader: asyncio.StreamReader,
        client_writer: asyncio.StreamWriter,
        client_ip: str,
        client_port: int
    ) -> Optional[Tuple[str, int, int, int]]:
        """
        处理SOCKS5协议
        
        Returns:
            Optional[Tuple[str, int, int, int]]: (target_host, target_port, bytes_sent, bytes_received) 或 None
        """
        try:
            # SOCKS5握手阶段
            # 格式: [VER(0x05), NMETHODS, METHODS...]
            nmethods = await client_reader.read(1)
            if not nmethods:
                return
            
            nmethods = nmethods[0]
            methods = await client_reader.read(nmethods)
            
            logger.debug("socks5_handshake", methods_count=nmethods, client=f"{client_ip}:{client_port}")
            
            # 检查是否需要认证
            # SOCKS5认证方法: 0x00=无认证, 0x02=用户名/密码认证
            if self.authenticator.is_enabled():
                # 检查客户端是否支持用户名/密码认证(0x02)
                if 0x02 not in methods:
                    logger.warning("socks5_auth_method_not_supported", client=f"{client_ip}:{client_port}")
                    # 返回无可接受的方法
                    client_writer.write(b'\x05\xFF')
                    await client_writer.drain()
                    return
                
                # 选择用户名/密码认证方法
                client_writer.write(b'\x05\x02')
                await client_writer.drain()
                
                # 执行用户名/密码认证
                # 格式: [VER(0x01), ULEN, UNAME, PLEN, PASSWD]
                auth_ver = await client_reader.read(1)
                if not auth_ver or auth_ver[0] != 0x01:
                    return
                
                # 读取用户名
                ulen = await client_reader.read(1)
                if not ulen:
                    return
                username_bytes = await client_reader.read(ulen[0])
                if len(username_bytes) != ulen[0]:
                    return
                username = username_bytes.decode('utf-8', errors='ignore')
                
                # 读取密码
                plen = await client_reader.read(1)
                if not plen:
                    return
                password_bytes = await client_reader.read(plen[0])
                if len(password_bytes) != plen[0]:
                    return
                password = password_bytes.decode('utf-8', errors='ignore')
                
                # 验证凭据
                if not self.authenticator.authenticate_socks5(username, password):
                    logger.warning("socks5_auth_failed", username=username, client=f"{client_ip}:{client_port}")
                    # 返回认证失败
                    client_writer.write(b'\x01\x01')  # VER=1, STATUS=1(失败)
                    await client_writer.drain()
                    return
                
                # 返回认证成功
                logger.info("socks5_auth_success", username=username, client=f"{client_ip}:{client_port}")
                client_writer.write(b'\x01\x00')  # VER=1, STATUS=0(成功)
                await client_writer.drain()
            else:
                # 无认证模式
                # 格式: [VER(0x05), METHOD(0x00)]
                client_writer.write(b'\x05\x00')
                await client_writer.drain()
            
            # SOCKS5连接请求阶段
            # 格式: [VER, CMD, RSV, ATYP, DST.ADDR, DST.PORT]
            request_header = await client_reader.read(4)
            if len(request_header) != 4:
                return
            
            ver, cmd, rsv, atyp = request_header
            
            if ver != 0x05:
                logger.error(f"不支持的SOCKS版本: {ver}")
                return
            
            if cmd != 0x01:  # 只支持CONNECT命令
                logger.error(f"不支持的SOCKS命令: {cmd}")
                # 返回命令不支持错误
                client_writer.write(b'\x05\x07\x00\x01\x00\x00\x00\x00\x00\x00')
                await client_writer.drain()
                return
            
            # 解析目标地址
            target_host, target_port = await self._parse_socks5_address(
                atyp, client_reader
            )
            
            if not target_host:
                logger.error("无法解析SOCKS5目标地址")
                # 返回地址类型不支持错误
                client_writer.write(b'\x05\x08\x00\x01\x00\x00\x00\x00\x00\x00')
                await client_writer.drain()
                return
            
            logger.info("socks5_connecting", target=f"{target_host}:{target_port}", client=f"{client_ip}:{client_port}")
            
            # 连接到目标服务器
            try:
                target_reader, target_writer = await asyncio.wait_for(
                    asyncio.open_connection(target_host, target_port),
                    timeout=self.config.connection_timeout
                )
            except asyncio.TimeoutError:
                logger.error(f"SOCKS5连接超时: {target_host}:{target_port}")
                # 返回TTL过期错误
                client_writer.write(b'\x05\x06\x00\x01\x00\x00\x00\x00\x00\x00')
                await client_writer.drain()
                return
            except Exception as e:
                logger.error(f"SOCKS5连接失败: {target_host}:{target_port} - {e}")
                # 返回连接被拒绝错误
                client_writer.write(b'\x05\x05\x00\x01\x00\x00\x00\x00\x00\x00')
                await client_writer.drain()
                return
            
            # 返回成功响应
            # 格式: [VER(0x05), REP(0x00=成功), RSV(0x00), ATYP(0x01=IPv4), 
            #        BND.ADDR(0.0.0.0), BND.PORT(0)]
            client_writer.write(b'\x05\x00\x00\x01\x00\x00\x00\x00\x00\x00')
            await client_writer.drain()
            
            logger.info("socks5_tunnel_established", target=f"{target_host}:{target_port}")
            
            # 进入数据转发阶段
            bytes_sent, bytes_received = await self._forward_data_with_stats(
                client_reader, client_writer,
                target_reader, target_writer
            )
            
            return (target_host, target_port, bytes_sent, bytes_received)
            
        except Exception as e:
            logger.error("socks5_error", error=str(e), exc_info=True)
            return None
    
    async def _parse_socks5_address(
        self,
        atyp: int,
        reader: asyncio.StreamReader
    ) -> Tuple[Optional[str], Optional[int]]:
        """解析SOCKS5地址"""
        try:
            if atyp == 0x01:  # IPv4
                addr_bytes = await reader.read(4)
                if len(addr_bytes) != 4:
                    return None, None
                host = '.'.join(str(b) for b in addr_bytes)
                
            elif atyp == 0x03:  # 域名
                domain_len = await reader.read(1)
                if not domain_len:
                    return None, None
                domain_len = domain_len[0]
                domain_bytes = await reader.read(domain_len)
                if len(domain_bytes) != domain_len:
                    return None, None
                host = domain_bytes.decode('utf-8')
                
            elif atyp == 0x04:  # IPv6
                addr_bytes = await reader.read(16)
                if len(addr_bytes) != 16:
                    return None, None
                # 简化IPv6处理
                import ipaddress
                host = str(ipaddress.IPv6Address(addr_bytes))
                
            else:
                logger.error(f"不支持的地址类型: {atyp}")
                return None, None
            
            # 读取端口(2字节,大端序)
            port_bytes = await reader.read(2)
            if len(port_bytes) != 2:
                return None, None
            port = struct.unpack('!H', port_bytes)[0]
            
            return host, port
            
        except Exception as e:
            logger.error(f"解析SOCKS5地址失败: {e}")
            return None, None
    
    async def start(self) -> None:
        """启动代理服务器"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.config.host,
            self.config.port
        )
        
        addr = self.server.sockets[0].getsockname()
        logger.info(f"代理服务器启动在 {addr[0]}:{addr[1]}")
        logger.info(f"支持协议: {', '.join(self.config.protocols).upper()}")
        logger.info(f"最大连接数: {self.config.max_connections}")
        logger.info(f"连接超时: {self.config.connection_timeout}秒")
        logger.info(f"HTTP/HTTPS: curl -x http://127.0.0.1:{self.config.port} http://www.baidu.com")
        logger.info(f"SOCKS5: curl --socks5 127.0.0.1:{self.config.port} http://www.baidu.com")
        
        async with self.server:
            await self.server.serve_forever()
    
    async def stop(self) -> None:
        """停止代理服务器"""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("代理服务器已停止")


async def main():
    """主函数(向后兼容)"""
    config = ProxyConfig()
    proxy = SimpleHTTPProxy(config)
    try:
        await proxy.start()
    except KeyboardInterrupt:
        logger.info("收到中断信号,正在停止...")
        await proxy.stop()


if __name__ == "__main__":
    asyncio.run(main())
