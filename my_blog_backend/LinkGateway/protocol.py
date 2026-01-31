import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class Request(BaseModel):
    """
    统一请求格式
    """
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="请求ID")
    service_id: Optional[str] = Field(None, description="目标服务ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="请求时间")
    action: str = Field(..., description="请求动作")
    data: Dict[str, Any] = Field(default_factory=dict, description="请求数据")
    auth: Optional[Dict[str, Any]] = Field(None, description="认证信息")
    
    class Config:
        """
        配置模型的配置
        """
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Response(BaseModel):
    """
    统一响应格式
    """
    request_id: str = Field(..., description="请求ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="响应时间")
    status: str = Field(..., description="响应状态，success表示成功，error表示失败")
    code: int = Field(..., description="响应码，200表示成功，其他表示失败")
    data: Dict[str, Any] = Field(default_factory=dict, description="响应数据")
    error: Optional[str] = Field(None, description="错误信息，仅在status为error时存在")
    
    class Config:
        """
        配置模型的配置
        """
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    @classmethod
    def success(cls, request_id: str, data: Dict[str, Any] = None) -> "Response":
        """
        创建成功响应
        
        Args:
            request_id: 请求ID
            data: 响应数据
            
        Returns:
            Response: 成功响应对象
        """
        return cls(
            request_id=request_id,
            status="success",
            code=200,
            data=data or {}
        )
    
    @classmethod
    def error(cls, request_id: str, code: int, error: str) -> "Response":
        """
        创建错误响应
        
        Args:
            request_id: 请求ID
            code: 响应码
            error: 错误信息
            
        Returns:
            Response: 错误响应对象
        """
        return cls(
            request_id=request_id,
            status="error",
            code=code,
            error=error,
            data={}
        )

class ServiceInfo(BaseModel):
    """
    服务信息模型
    """
    service_id: str = Field(..., description="服务ID")
    service_name: str = Field(..., description="服务名称")
    version: str = Field(..., description="服务版本")
    engine_type: str = Field(..., description="引擎类型")
    status: str = Field(..., description="服务状态")
    description: Optional[str] = Field(None, description="服务描述")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="更新时间")
    
    class Config:
        """
        配置模型的配置
        """
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class APIInfo(BaseModel):
    """
    API信息模型
    """
    path: str = Field(..., description="API路径")
    methods: list[str] = Field(..., description="HTTP方法列表")
    service_id: str = Field(..., description="所属服务ID")
    endpoint: str = Field(..., description="处理函数名称")
    description: Optional[str] = Field(None, description="API描述")
    
    class Config:
        """
        配置模型的配置
        """
        allow_population_by_field_name = True
