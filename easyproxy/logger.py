"""结构化日志系统"""

import logging
import sys
from pathlib import Path
from typing import Optional
import structlog
from structlog.types import EventDict, WrappedLogger


def add_log_level(
    logger: WrappedLogger, method_name: str, event_dict: EventDict
) -> EventDict:
    """添加日志级别到事件字典"""
    if method_name == "warn":
        method_name = "warning"
    event_dict["level"] = method_name.upper()
    return event_dict


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    json_format: bool = False
) -> None:
    """
    配置结构化日志系统
    
    Args:
        log_level: 日志级别
        log_file: 日志文件路径,None表示输出到控制台
        json_format: 是否使用JSON格式输出
    """
    # 配置标准库logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )
    
    # 如果指定了日志文件
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(getattr(logging, log_level.upper()))
        logging.root.addHandler(file_handler)
    
    # 配置structlog处理器链
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
    ]
    
    if json_format:
        # JSON格式输出(生产环境)
        processors.extend([
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer()
        ])
    else:
        # 彩色控制台输出(开发环境)
        processors.extend([
            structlog.processors.ExceptionPrettyPrinter(),
            structlog.dev.ConsoleRenderer(colors=True)
        ])
    
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    获取结构化日志记录器
    
    Args:
        name: 日志记录器名称
    
    Returns:
        structlog.stdlib.BoundLogger: 日志记录器
    """
    return structlog.get_logger(name)


class AccessLogger:
    """访问日志记录器"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.logger = get_logger("easyproxy.access")
    
    def log_request(
        self,
        client_ip: str,
        client_port: int,
        protocol: str,
        target_host: str,
        target_port: int,
        status: str = "success",
        bytes_sent: int = 0,
        bytes_received: int = 0,
        duration_ms: float = 0,
        error: Optional[str] = None
    ) -> None:
        """
        记录访问日志
        
        Args:
            client_ip: 客户端IP
            client_port: 客户端端口
            protocol: 协议类型
            target_host: 目标主机
            target_port: 目标端口
            status: 连接状态
            bytes_sent: 发送字节数
            bytes_received: 接收字节数
            duration_ms: 连接持续时间(毫秒)
            error: 错误信息
        """
        if not self.enabled:
            return
        
        log_data = {
            "client": f"{client_ip}:{client_port}",
            "protocol": protocol,
            "target": f"{target_host}:{target_port}",
            "status": status,
            "bytes_sent": bytes_sent,
            "bytes_received": bytes_received,
            "duration_ms": round(duration_ms, 2),
        }
        
        if error:
            log_data["error"] = error
            self.logger.warning("proxy_request_failed", **log_data)
        else:
            self.logger.info("proxy_request", **log_data)


class ConnectionStats:
    """连接统计"""
    
    def __init__(self):
        self.total_connections = 0
        self.active_connections = 0
        self.total_bytes_sent = 0
        self.total_bytes_received = 0
        self.connections_by_protocol = {
            "http": 0,
            "https": 0,
            "socks5": 0
        }
        self.error_count = 0
        self.logger = get_logger("easyproxy.stats")
    
    def increment_connection(self, protocol: str) -> None:
        """增加连接计数"""
        self.total_connections += 1
        self.active_connections += 1
        if protocol.lower() in self.connections_by_protocol:
            self.connections_by_protocol[protocol.lower()] += 1
    
    def decrement_connection(self) -> None:
        """减少活跃连接计数"""
        self.active_connections = max(0, self.active_connections - 1)
    
    def add_traffic(self, bytes_sent: int, bytes_received: int) -> None:
        """添加流量统计"""
        self.total_bytes_sent += bytes_sent
        self.total_bytes_received += bytes_received
    
    def increment_error(self) -> None:
        """增加错误计数"""
        self.error_count += 1
    
    def log_stats(self) -> None:
        """记录统计信息"""
        self.logger.info(
            "connection_stats",
            total_connections=self.total_connections,
            active_connections=self.active_connections,
            total_bytes_sent=self.total_bytes_sent,
            total_bytes_received=self.total_bytes_received,
            http_connections=self.connections_by_protocol["http"],
            https_connections=self.connections_by_protocol["https"],
            socks5_connections=self.connections_by_protocol["socks5"],
            error_count=self.error_count
        )
    
    def get_stats_dict(self) -> dict:
        """获取统计信息字典"""
        return {
            "total_connections": self.total_connections,
            "active_connections": self.active_connections,
            "total_bytes_sent": self.total_bytes_sent,
            "total_bytes_received": self.total_bytes_received,
            "connections_by_protocol": self.connections_by_protocol.copy(),
            "error_count": self.error_count
        }
