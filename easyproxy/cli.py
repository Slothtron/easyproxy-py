"""命令行接口"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click

from .config import ProxyConfig, load_config, create_default_config
from .proxy import SimpleHTTPProxy


@click.group()
@click.version_option(version="0.3.0")
def cli():
    """EasyProxy - 多协议代理服务器"""
    pass


@cli.command()
@click.option(
    "-c", "--config",
    type=click.Path(exists=True, path_type=Path),
    help="配置文件路径"
)
@click.option(
    "-H", "--host",
    type=str,
    help="监听地址 (覆盖配置文件)"
)
@click.option(
    "-p", "--port",
    type=int,
    help="监听端口 (覆盖配置文件)"
)
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    help="日志级别 (覆盖配置文件)"
)
@click.option(
    "-l", "--log-file",
    type=click.Path(path_type=Path),
    help="日志文件路径 (覆盖配置文件)"
)
def start(
    config: Optional[Path],
    host: Optional[str],
    port: Optional[int],
    log_level: Optional[str],
    log_file: Optional[Path]
):
    """启动代理服务器"""
    
    # 加载配置
    if config:
        click.echo(f"从配置文件加载: {config}")
        proxy_config = load_config(config)
    else:
        click.echo("使用默认配置")
        proxy_config = ProxyConfig()
    
    # 命令行参数覆盖配置文件
    if host:
        proxy_config.host = host
    if port:
        proxy_config.port = port
    if log_level:
        proxy_config.log_level = log_level.upper()
    if log_file:
        proxy_config.log_file = str(log_file)
    
    # 显示配置信息
    click.echo(f"监听地址: {proxy_config.host}:{proxy_config.port}")
    click.echo(f"支持协议: {', '.join(proxy_config.protocols).upper()}")
    click.echo(f"日志级别: {proxy_config.log_level}")
    if proxy_config.log_file:
        click.echo(f"日志文件: {proxy_config.log_file}")
    click.echo("")
    
    # 启动代理服务器
    try:
        proxy = SimpleHTTPProxy(proxy_config)
        asyncio.run(proxy.start())
    except KeyboardInterrupt:
        click.echo("\n收到中断信号,正在停止...")
        sys.exit(0)
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("output", type=click.Path(path_type=Path))
def init(output: Path):
    """生成默认配置文件"""
    
    if output.exists():
        if not click.confirm(f"文件 {output} 已存在,是否覆盖?"):
            click.echo("操作已取消")
            return
    
    try:
        create_default_config(output)
        click.echo(f"配置文件已生成: {output}")
        click.echo(f"使用方式: easyproxy start -c {output}")
    except Exception as e:
        click.echo(f"错误: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "-c", "--config",
    type=click.Path(exists=True, path_type=Path),
    help="配置文件路径"
)
def validate(config: Optional[Path]):
    """验证配置文件"""
    
    if not config:
        click.echo("错误: 请指定配置文件路径", err=True)
        sys.exit(1)
    
    try:
        proxy_config = load_config(config)
        click.echo(f"✓ 配置文件有效: {config}")
        click.echo("")
        click.echo("配置详情:")
        click.echo(f"  监听地址: {proxy_config.host}:{proxy_config.port}")
        click.echo(f"  支持协议: {', '.join(proxy_config.protocols)}")
        click.echo(f"  最大连接数: {proxy_config.max_connections}")
        click.echo(f"  连接超时: {proxy_config.connection_timeout}秒")
        click.echo(f"  日志级别: {proxy_config.log_level}")
        if proxy_config.log_file:
            click.echo(f"  日志文件: {proxy_config.log_file}")
    except Exception as e:
        click.echo(f"✗ 配置文件无效: {e}", err=True)
        sys.exit(1)


def main():
    """主入口函数"""
    cli()


if __name__ == "__main__":
    main()
