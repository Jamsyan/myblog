from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from .base import BaseEngine

class EngineRegistry(ABC):
    """
    引擎注册规范，定义引擎注册的流程和验证逻辑
    """
    
    def __init__(self):
        self.registry: Dict[str, BaseEngine] = {}
    
    @abstractmethod
    def register_engine(self, engine: BaseEngine) -> bool:
        """
        注册引擎
        
        Args:
            engine: 要注册的引擎实例
            
        Returns:
            bool: 注册成功返回True，失败返回False
        """
        pass
    
    @abstractmethod
    def unregister_engine(self, service_id: str) -> bool:
        """
        注销引擎
        
        Args:
            service_id: 引擎的服务ID
            
        Returns:
            bool: 注销成功返回True，失败返回False
        """
        pass
    
    @abstractmethod
    def get_engine(self, service_id: str) -> Optional[BaseEngine]:
        """
        根据服务ID获取引擎
        
        Args:
            service_id: 引擎的服务ID
            
        Returns:
            Optional[BaseEngine]: 找到的引擎实例，未找到返回None
        """
        pass
    
    @abstractmethod
    def get_engine_by_name(self, service_name: str, version: Optional[str] = None) -> Optional[BaseEngine]:
        """
        根据服务名称获取引擎
        
        Args:
            service_name: 服务名称
            version: 服务版本，不指定则返回最新版本
            
        Returns:
            Optional[BaseEngine]: 找到的引擎实例，未找到返回None
        """
        pass
    
    @abstractmethod
    def list_engines(self, engine_type: Optional[str] = None) -> List[BaseEngine]:
        """
        列出所有注册的引擎
        
        Args:
            engine_type: 引擎类型，不指定则返回所有类型
            
        Returns:
            List[BaseEngine]: 引擎实例列表
        """
        pass
    
    def validate_engine(self, engine: BaseEngine) -> bool:
        """
        验证引擎是否符合注册要求
        
        Args:
            engine: 要验证的引擎实例
            
        Returns:
            bool: 验证通过返回True，失败返回False
        """
        # 检查引擎是否继承自BaseEngine
        if not isinstance(engine, BaseEngine):
            return False
        
        # 检查必要的属性是否存在
        required_attrs = ["service_id", "service_name", "version", "engine_type", "status"]
        for attr in required_attrs:
            if not hasattr(engine, attr):
                return False
        
        # 检查引擎类型是否有效
        valid_engine_types = [BaseEngine.EngineType.KERNEL, BaseEngine.EngineType.NETWORK]
        if engine.engine_type not in valid_engine_types:
            return False
        
        # 检查状态是否有效
        valid_statuses = [
            BaseEngine.Status.STOPPED,
            BaseEngine.Status.STARTING,
            BaseEngine.Status.RUNNING,
            BaseEngine.Status.STOPPING,
            BaseEngine.Status.ERROR
        ]
        if engine.status not in valid_statuses:
            return False
        
        # 检查必要的方法是否实现
        required_methods = [
            "start", "stop", "handle_request", 
            "get_api_routes", "get_dependencies", "health_check"
        ]
        for method in required_methods:
            if not hasattr(engine, method) or not callable(getattr(engine, method)):
                return False
        
        # 检查服务名称是否已存在
        for registered_engine in self.registry.values():
            if registered_engine.service_name == engine.service_name and registered_engine.version == engine.version:
                return False
        
        # 验证引擎配置
        if not engine.validate_config():
            return False
        
        return True
    
    def validate_engine_compatibility(self, engine: BaseEngine, min_version: str = "1.0.0") -> bool:
        """
        验证引擎版本兼容性
        
        Args:
            engine: 要验证的引擎实例
            min_version: 最低兼容版本
            
        Returns:
            bool: 兼容返回True，否则返回False
        """
        return engine.is_compatible(min_version)
    
    def get_engine_metadata(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        获取引擎元数据
        
        Args:
            service_id: 引擎的服务ID
            
        Returns:
            Optional[Dict[str, Any]]: 引擎元数据，未找到返回None
        """
        engine = self.get_engine(service_id)
        if engine:
            return engine.get_metadata()
        return None
    
    def get_all_engines_metadata(self, engine_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取所有引擎的元数据
        
        Args:
            engine_type: 引擎类型，不指定则返回所有类型
            
        Returns:
            List[Dict[str, Any]]: 引擎元数据列表
        """
        engines = self.list_engines(engine_type)
        return [engine.get_metadata() for engine in engines]
    
    def check_engine_health(self, service_id: str) -> Dict[str, Any]:
        """
        检查引擎健康状态
        
        Args:
            service_id: 引擎的服务ID
            
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        engine = self.get_engine(service_id)
        if engine:
            try:
                return engine.health_check()
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"健康检查失败: {str(e)}"
                }
        return {
            "status": "error",
            "message": "引擎未找到"
        }
    
    def check_all_engines_health(self, engine_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        检查所有引擎的健康状态
        
        Args:
            engine_type: 引擎类型，不指定则检查所有类型
            
        Returns:
            List[Dict[str, Any]]: 健康检查结果列表
        """
        engines = self.list_engines(engine_type)
        health_results = []
        
        for engine in engines:
            try:
                result = engine.health_check()
                result["service_id"] = engine.service_id
                result["service_name"] = engine.service_name
                result["version"] = engine.version
                health_results.append(result)
            except Exception as e:
                health_results.append({
                    "service_id": engine.service_id,
                    "service_name": engine.service_name,
                    "version": engine.version,
                    "status": "error",
                    "message": f"健康检查失败: {str(e)}"
                })
        
        return health_results
