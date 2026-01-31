import json
from typing import Dict, Any, List

class ServiceStandard:
    """
    服务标准定义类，用于验证服务配置文件的格式
    """
    
    # 服务配置文件必填字段
    REQUIRED_FIELDS = [
        "service_id",
        "service_name",
        "version"
    ]
    
    # 服务配置文件可选字段
    OPTIONAL_FIELDS = [
        "description",
        "apis",
        "database",
        "dependencies"
    ]
    
    # 数据库配置必填字段
    DATABASE_REQUIRED_FIELDS = [
        "type"
    ]
    
    # 数据库配置可选字段
    DATABASE_OPTIONAL_FIELDS = [
        "name",
        "host",
        "port",
        "username",
        "password",
        "database"
    ]
    
    # API配置必填字段
    API_REQUIRED_FIELDS = [
        "path",
        "method"
    ]
    
    # API配置可选字段
    API_OPTIONAL_FIELDS = [
        "description",
        "tags",
        "responses",
        "request_body",
        "parameters"
    ]
    
    @classmethod
    def validate_service_json(cls, service_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证服务配置文件格式
        
        Args:
            service_json: 服务配置文件内容
            
        Returns:
            Dict[str, Any]: 验证结果，包含valid和reason字段
        """
        if not cls._check_required_fields(service_json, cls.REQUIRED_FIELDS):
            return {"valid": False, "reason": "Missing required fields"}
        
        if not cls._check_service_id_format(service_json):
            return {"valid": False, "reason": "Invalid service_id format"}
        
        if "database" in service_json:
            result = cls._validate_database_config(service_json["database"])
            if not result["valid"]:
                return result
        
        if "apis" in service_json:
            result = cls._validate_apis_config(service_json["apis"])
            if not result["valid"]:
                return result
        
        return {"valid": True, "reason": "Service JSON format is valid"}
    
    @classmethod
    def _check_required_fields(cls, config: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """
        检查必填字段
        
        Args:
            config: 配置字典
            required_fields: 必填字段列表
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        for field in required_fields:
            if field not in config:
                return {"valid": False, "reason": f"Missing required field: {field}"}
        return {"valid": True}
    
    @classmethod
    def _check_service_id_format(cls, service_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查service_id格式
        
        Args:
            service_json: 服务配置
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        service_id = service_json.get("service_id")
        if not service_id:
            return {"valid": False, "reason": "Missing service_id"}
        return {"valid": True}
    
    @classmethod
    def _validate_database_config(cls, database_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证数据库配置
        
        Args:
            database_config: 数据库配置
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(database_config, dict):
            return {"valid": False, "reason": "Database config must be a dictionary"}
        
        result = cls._check_required_fields(database_config, cls.DATABASE_REQUIRED_FIELDS)
        if not result["valid"]:
            return result
        
        db_type = database_config.get("type")
        if not db_type:
            return {"valid": False, "reason": "Missing database type"}
        
        if db_type not in ["sqlite", "mysql", "postgresql"]:
            return {"valid": False, "reason": f"Unsupported database type: {db_type}"}
        
        return {"valid": True}
    
    @classmethod
    def _validate_apis_config(cls, apis: Any, is_engine: bool = False) -> Dict[str, Any]:
        """
        验证API配置
        
        Args:
            apis: API配置列表
            is_engine: 是否为引擎配置
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(apis, list):
            return {"valid": False, "reason": "APIs must be a list"}
        
        required_fields = cls.ENGINE_API_REQUIRED_FIELDS if is_engine else cls.API_REQUIRED_FIELDS
        
        for i, api in enumerate(apis):
            result = cls._check_required_fields(api, required_fields)
            if not result["valid"]:
                return result
        
        return {"valid": True}
    
    @classmethod
    def get_default_service_json(cls, service_id: str, service_name: str, version: str) -> Dict[str, Any]:
        """
        获取默认的服务配置文件模板
        
        Args:
            service_id: 服务ID
            service_name: 服务名称
            version: 服务版本
            
        Returns:
            Dict[str, Any]: 默认的服务配置文件模板
        """
        return {
            "service_id": service_id,
            "service_name": service_name,
            "version": version,
            "description": "",
            "apis": [],
            "database": {
                "type": "sqlite",
                "name": service_id
            },
            "dependencies": []
        }

class EngineStandard:
    """
    引擎标准定义类，用于验证引擎配置文件的格式
    """
    
    # 引擎配置文件必填字段
    REQUIRED_FIELDS = [
        "service_id",
        "service_name",
        "version",
        "engine_type"
    ]
    
    # 引擎配置文件可选字段
    OPTIONAL_FIELDS = [
        "description",
        "apis",
        "database",
        "dependencies"
    ]
    
    # 引擎类型枚举
    ENGINE_TYPES = [
        "network",
        "kernel"
    ]
    
    @classmethod
    def validate_engine_json(cls, engine_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证引擎配置文件格式
        
        Args:
            engine_json: 引擎配置文件内容
            
        Returns:
            Dict[str, Any]: 验证结果，包含valid和reason字段
        """
        if not cls._check_required_fields(engine_json, cls.REQUIRED_FIELDS):
            return {"valid": False, "reason": "Missing required fields"}
        
        if not cls._check_engine_type(engine_json):
            return {"valid": False, "reason": "Invalid engine type"}
        
        if "database" in engine_json:
            result = cls._validate_database_config(engine_json["database"])
            if not result["valid"]:
                return result
        
        if "apis" in engine_json:
            result = cls._validate_apis_config(engine_json["apis"], is_engine=True)
            if not result["valid"]:
                return result
        
        return {"valid": True, "reason": "Engine JSON format is valid"}
    
    @classmethod
    def _check_required_fields(cls, config: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """
        检查必填字段
        
        Args:
            config: 配置字典
            required_fields: 必填字段列表
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        for field in required_fields:
            if field not in config:
                return {"valid": False, "reason": f"Missing required field: {field}"}
        return {"valid": True}
    
    @classmethod
    def _check_engine_type(cls, engine_json: Dict[str, Any]) -> Dict[str, Any]:
        """
        检查引擎类型
        
        Args:
            engine_json: 引擎配置
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        engine_type = engine_json.get("engine_type", "").lower()
        if engine_type not in cls.ENGINE_TYPES:
            return {"valid": False, "reason": f"Invalid engine type: {engine_type}. Must be one of {', '.join(cls.ENGINE_TYPES)}"}
        return {"valid": True}
    
    @classmethod
    def _validate_database_config(cls, database_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证数据库配置
        
        Args:
            database_config: 数据库配置
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(database_config, dict):
            return {"valid": False, "reason": "Database config must be a dictionary"}
        
        result = cls._check_required_fields(database_config, cls.DATABASE_REQUIRED_FIELDS)
        if not result["valid"]:
            return result
        
        db_type = database_config.get("type")
        if not db_type:
            return {"valid": False, "reason": "Missing database type"}
        
        if db_type not in ["sqlite", "mysql", "postgresql"]:
            return {"valid": False, "reason": f"Unsupported database type: {db_type}"}
        
        return {"valid": True}
    
    @classmethod
    def _validate_apis_config(cls, apis: Any, is_engine: bool = False) -> Dict[str, Any]:
        """
        验证API配置
        
        Args:
            apis: API配置列表
            is_engine: 是否为引擎配置
            
        Returns:
            Dict[str, Any]: 验证结果
        """
        if not isinstance(apis, list):
            return {"valid": False, "reason": "APIs must be a list"}
        
        required_fields = cls.ENGINE_API_REQUIRED_FIELDS if is_engine else cls.API_REQUIRED_FIELDS
        
        for i, api in enumerate(apis):
            result = cls._check_required_fields(api, required_fields)
            if not result["valid"]:
                return result
        
        return {"valid": True}
    
    @classmethod
    def get_default_engine_json(cls, service_id: str, service_name: str, version: str, engine_type: str) -> Dict[str, Any]:
        """
        获取默认的引擎配置文件模板
        
        Args:
            service_id: 服务ID
            service_name: 服务名称
            version: 服务版本
            engine_type: 引擎类型
            
        Returns:
            Dict[str, Any]: 默认的引擎配置文件模板
        """
        return {
            "service_id": service_id,
            "service_name": service_name,
            "version": version,
            "engine_type": engine_type,
            "description": "",
            "apis": [],
            "database": {
                "type": "sqlite",
                "name": service_id
            },
            "dependencies": []
        }

class APIStandard:
    """
    API标准定义类，用于验证API配置的格式
    """
    
    # API路径前缀
    SERVICE_API_PREFIX = "/api/{service_id}"
    ENGINE_API_PREFIX = "/api/{engine_name}"
    
    # 支持的HTTP方法
    SUPPORTED_METHODS = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
        "HEAD"
    ]
    
    @classmethod
    def format_api_path(cls, service_type: str, service_id: str, path: str) -> str:
        """
        格式化API路径，确保符合标准格式
        
        Args:
            service_type: 服务类型，"business"或"engine"
            service_id: 服务ID
            path: API路径
            
        Returns:
            str: 格式化后的API路径
        """
        # 如果路径已经包含前缀，直接返回
        if path.startswith(f"/api/{service_id}"):
            return path
        
        # 确保路径以/开头
        if not path.startswith("/"):
            path = f"/{path}"
        
        # 根据服务类型添加前缀
        if service_type == "business":
            return f"{cls.SERVICE_API_PREFIX.format(service_id=service_id)}{path}"
        elif service_type == "engine":
            return f"{cls.ENGINE_API_PREFIX.format(engine_name=service_id)}{path}"
        
        return path
    
    @classmethod
    def validate_api_method(cls, method: str) -> bool:
        """
        验证HTTP方法是否支持
        
        Args:
            method: HTTP方法
            
        Returns:
            bool: 支持返回True，不支持返回False
        """
        return method.upper() in cls.SUPPORTED_METHODS
    
    @classmethod
    def normalize_api_method(cls, method: str) -> str:
        """
        标准化HTTP方法，转换为大写
        
        Args:
            method: HTTP方法
            
        Returns:
            str: 标准化后的HTTP方法
        """
        return method.upper()
