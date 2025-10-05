"""认证模块"""

from typing import Optional, Tuple
import base64
from .config import AuthConfig
from .logger import get_logger

logger = get_logger(__name__)


class Authenticator:
    """认证器基类"""
    
    def __init__(self, config: AuthConfig):
        self.config = config
    
    def is_enabled(self) -> bool:
        """检查认证是否启用"""
        return self.config.enabled
    
    def authenticate(self, credentials: dict) -> bool:
        """
        认证用户
        
        Args:
            credentials: 认证凭据
        
        Returns:
            bool: 认证是否成功
        """
        raise NotImplementedError


class BasicAuthenticator(Authenticator):
    """Basic Auth认证器"""
    
    def authenticate_http(self, auth_header: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        HTTP Basic Auth认证
        
        Args:
            auth_header: Authorization头的值
        
        Returns:
            Tuple[bool, Optional[str]]: (是否认证成功, 用户名)
        """
        if not self.config.enabled:
            return (True, None)
        
        # 解析认证头
        credentials = self.config.parse_basic_auth(auth_header)
        if not credentials:
            logger.warning("auth_failed", reason="invalid_auth_header")
            return (False, None)
        
        username, password = credentials
        
        # 验证凭据
        if self.config.verify_credentials(username, password):
            logger.info("auth_success", username=username)
            return (True, username)
        else:
            logger.warning("auth_failed", username=username, reason="invalid_credentials")
            return (False, username)
    
    def authenticate_socks5(self, username: str, password: str) -> bool:
        """
        SOCKS5认证
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            bool: 认证是否成功
        """
        if not self.config.enabled:
            return True
        
        if self.config.verify_credentials(username, password):
            logger.info("socks5_auth_success", username=username)
            return True
        else:
            logger.warning("socks5_auth_failed", username=username)
            return False
    
    def generate_http_challenge(self) -> str:
        """
        生成HTTP认证挑战
        
        Returns:
            str: WWW-Authenticate头的值
        """
        return self.config.generate_auth_challenge()
    
    def generate_http_401_response(self) -> bytes:
        """
        生成HTTP 401未授权响应
        
        Returns:
            bytes: HTTP响应
        """
        challenge = self.generate_http_challenge()
        response = (
            "HTTP/1.1 407 Proxy Authentication Required\r\n"
            f"Proxy-Authenticate: {challenge}\r\n"
            "Content-Type: text/plain\r\n"
            "Content-Length: 39\r\n"
            "Connection: close\r\n"
            "\r\n"
            "Proxy Authentication Required\r\n"
        )
        return response.encode('utf-8')


class NoAuthenticator(Authenticator):
    """无认证器"""
    
    def authenticate(self, credentials: dict) -> bool:
        """总是返回True"""
        return True
    
    def authenticate_http(self, auth_header: Optional[str]) -> Tuple[bool, Optional[str]]:
        """总是返回True"""
        return (True, None)
    
    def authenticate_socks5(self, username: str, password: str) -> bool:
        """总是返回True"""
        return True


def create_authenticator(config: Optional[AuthConfig]) -> Authenticator:
    """
    创建认证器
    
    Args:
        config: 认证配置
    
    Returns:
        Authenticator: 认证器实例
    """
    if not config or not config.enabled:
        # 创建一个禁用的配置
        disabled_config = AuthConfig(enabled=False)
        return NoAuthenticator(disabled_config)
    
    if config.type == "basic":
        return BasicAuthenticator(config)
    else:
        return NoAuthenticator(config)
