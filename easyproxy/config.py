"""配置管理模块"""

from typing import Optional, List, Dict
from pathlib import Path
import yaml
import base64
import hashlib
from pydantic import BaseModel, Field, field_validator


class AuthConfig(BaseModel):
    """认证配置"""
    enabled: bool = Field(default=False, description="是否启用认证")
    type: str = Field(
        default="basic",
        pattern="^(basic|none)$",
        description="认证类型: basic(基本认证), none(无认证)"
    )
    users: Dict[str, str] = Field(
        default_factory=dict,
        description="用户名密码映射 (明文密码,启动时会自动加密)"
    )
    realm: str = Field(
        default="EasyProxy",
        description="认证域名(用于Basic Auth)"
    )
    
    @field_validator("users")
    @classmethod
    def validate_users(cls, v: Dict[str, str]) -> Dict[str, str]:
        """验证用户配置"""
        if not v:
            return v
        
        # 检查用户名和密码是否为空
        for username, password in v.items():
            if not username or not isinstance(username, str):
                raise ValueError("用户名不能为空")
            if not password or not isinstance(password, str):
                raise ValueError(f"用户 {username} 的密码不能为空")
        
        return v
    
    def verify_credentials(self, username: str, password: str) -> bool:
        """
        验证用户凭据
        
        Args:
            username: 用户名
            password: 密码
        
        Returns:
            bool: 验证是否成功
        """
        if not self.enabled:
            return True
        
        if username not in self.users:
            return False
        
        return self.users[username] == password
    
    def parse_basic_auth(self, auth_header: str) -> Optional[tuple[str, str]]:
        """
        解析Basic Auth头
        
        Args:
            auth_header: Authorization头的值
        
        Returns:
            Optional[tuple[str, str]]: (username, password) 或 None
        """
        if not auth_header:
            return None
        
        # Basic Auth格式: "Basic base64(username:password)"
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'basic':
            return None
        
        try:
            # 解码base64
            decoded = base64.b64decode(parts[1]).decode('utf-8')
            if ':' not in decoded:
                return None
            
            username, password = decoded.split(':', 1)
            return (username, password)
        except Exception:
            return None
    
    def generate_auth_challenge(self) -> str:
        """
        生成认证挑战响应头
        
        Returns:
            str: WWW-Authenticate头的值
        """
        return f'Basic realm="{self.realm}"'


class ProxyConfig(BaseModel):
    """代理服务器配置"""
    
    # 服务器配置
    host: str = Field(default="0.0.0.0", description="监听地址")
    port: int = Field(default=7899, ge=1, le=65535, description="监听端口")
    
    # 协议配置
    protocols: List[str] = Field(
        default=["http", "https", "socks5"],
        description="启用的协议列表"
    )
    
    # 连接配置
    max_connections: int = Field(default=1000, ge=1, description="最大并发连接数")
    connection_timeout: int = Field(default=30, ge=1, description="连接超时(秒)")
    idle_timeout: int = Field(default=300, ge=1, description="空闲超时(秒)")
    buffer_size: int = Field(default=8192, ge=512, description="缓冲区大小(字节)")
    
    # 日志配置
    log_level: str = Field(
        default="INFO",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$",
        description="日志级别"
    )
    access_log: bool = Field(default=True, description="是否记录访问日志")
    log_file: Optional[str] = Field(default=None, description="日志文件路径")
    
    # 认证配置(可选)
    auth: Optional[AuthConfig] = None
    
    @field_validator("protocols")
    @classmethod
    def validate_protocols(cls, v: List[str]) -> List[str]:
        """验证协议列表"""
        valid_protocols = {"http", "https", "socks5"}
        for protocol in v:
            if protocol.lower() not in valid_protocols:
                raise ValueError(
                    f"不支持的协议: {protocol}. "
                    f"支持的协议: {', '.join(valid_protocols)}"
                )
        return [p.lower() for p in v]
    
    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "ProxyConfig":
        """从YAML文件加载配置"""
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if data is None:
            data = {}
        
        return cls(**data)
    
    @classmethod
    def from_dict(cls, data: dict) -> "ProxyConfig":
        """从字典创建配置"""
        return cls(**data)
    
    def to_yaml(self, config_path: str | Path) -> None:
        """保存配置到YAML文件"""
        config_path = Path(config_path)
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.safe_dump(
                self.model_dump(exclude_none=True),
                f,
                default_flow_style=False,
                allow_unicode=True
            )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return self.model_dump(exclude_none=True)


def load_config(config_path: Optional[str | Path] = None) -> ProxyConfig:
    """
    加载配置
    
    Args:
        config_path: 配置文件路径,如果为None则使用默认配置
    
    Returns:
        ProxyConfig: 配置对象
    """
    if config_path is None:
        # 返回默认配置
        return ProxyConfig()
    
    return ProxyConfig.from_yaml(config_path)


def create_default_config(config_path: str | Path) -> None:
    """
    创建默认配置文件
    
    Args:
        config_path: 配置文件保存路径
    """
    config = ProxyConfig()
    config.to_yaml(config_path)
