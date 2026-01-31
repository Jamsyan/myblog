from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class DatabaseConfig(BaseModel):
    """
    数据库配置模型
    """
    type: str = Field(..., description="数据库类型，如sqlite、mysql、postgresql等")
    path: Optional[str] = Field(None, description="SQLite数据库路径")
    host: Optional[str] = Field(None, description="数据库主机地址")
    port: Optional[int] = Field(None, description="数据库端口")
    username: Optional[str] = Field(None, description="数据库用户名")
    password: Optional[str] = Field(None, description="数据库密码")
    database: Optional[str] = Field(None, description="数据库名称")

class EngineConfig(BaseModel):
    """
    引擎配置模型
    """
    service_name: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    description: Optional[str] = Field(None, description="服务描述")
    engine_type: str = Field("kernel", description="引擎类型，kernel表示内核引擎，network表示网络引擎")
    database: Optional[DatabaseConfig] = Field(None, description="数据库配置")
    api_prefix: str = Field("", description="API路由前缀")
    enabled: bool = Field(True, description="是否启用该引擎")
    log_level: str = Field("INFO", description="日志级别")
    
    class Config:
        """
        配置模型的配置
        """
        extra = "allow"  # 允许额外的配置项

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持嵌套路径
        
        Args:
            key: 配置键，支持点分隔的嵌套路径，如 "database.host"
            default: 默认值
            
        Returns:
            Any: 配置值
        """
        keys = key.split(".")
        value = self.dict()
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
