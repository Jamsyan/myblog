from typing import Dict, Any, List

from BaseEngine.engine_interface import EngineInterface


class APIRoutes:
    """
    API路由类，负责定义引擎的API路由
    """
    
    def __init__(self, engine):
        """
        初始化API路由
        
        Args:
            engine: 引擎实例
        """
        self.engine = engine
    
    def get_api_routes(self) -> List[Dict[str, Any]]:
        """
        获取引擎的API路由定义
        
        Returns:
            List[Dict[str, Any]]: API路由定义列表
        """
        return [
            {
                "path": "/register-operation",
                "methods": ["POST"],
                "endpoint": self._api_register_operation,
                "description": "注册可执行操作"
            },
            {
                "path": "/register-component",
                "methods": ["POST"],
                "endpoint": self._api_register_component,
                "description": "注册前端组件"
            },
            {
                "path": "/get-default-permission",
                "methods": ["POST"],
                "endpoint": self._api_get_default_permission,
                "description": "获取默认权限等级"
            },
            {
                "path": "/check-operation-permission",
                "methods": ["POST"],
                "endpoint": self._api_check_operation_permission,
                "description": "检查用户是否有权执行操作"
            },
            {
                "path": "/check-component-permission",
                "methods": ["POST"],
                "endpoint": self._api_check_component_permission,
                "description": "检查用户是否有权访问组件"
            },
            {
                "path": "/get-permission-config",
                "methods": ["POST"],
                "endpoint": self._api_get_permission_config,
                "description": "获取指定权限等级的配置"
            },
            {
                "path": "/update-permission-config",
                "methods": ["POST"],
                "endpoint": self._api_update_permission_config,
                "description": "更新权限配置"
            },
            {
                "path": "/set-default-permission",
                "methods": ["POST"],
                "endpoint": self._api_set_default_permission,
                "description": "设置默认权限等级"
            },
            {
                "path": "/reload-permissions",
                "methods": ["POST"],
                "endpoint": self._api_reload_permissions,
                "description": "重新加载所有权限配置到内存（仅P0级用户可用）"
            }
        ]
    
    # API端点方法，用于FastAPI路由
    async def _api_register_operation(self, request: dict):
        """
        API端点：注册可执行操作
        """
        return self.engine.handle_request("register_operation", request)
    
    async def _api_register_component(self, request: dict):
        """
        API端点：注册前端组件
        """
        return self.engine.handle_request("register_component", request)
    
    async def _api_get_default_permission(self, request: dict):
        """
        API端点：获取默认权限等级
        """
        return self.engine.handle_request("get_default_permission", request)
    
    async def _api_check_operation_permission(self, request: dict):
        """
        API端点：检查用户是否有权执行操作
        """
        return self.engine.handle_request("check_operation_permission", request)
    
    async def _api_check_component_permission(self, request: dict):
        """
        API端点：检查用户是否有权访问组件
        """
        return self.engine.handle_request("check_component_permission", request)
    
    async def _api_get_permission_config(self, request: dict):
        """
        API端点：获取指定权限等级的配置
        """
        return self.engine.handle_request("get_permission_config", request)
    
    async def _api_update_permission_config(self, request: dict):
        """
        API端点：更新权限配置
        """
        return self.engine.handle_request("update_permission_config", request)
    
    async def _api_set_default_permission(self, request: dict):
        """
        API端点：设置默认权限等级
        """
        return self.engine.handle_request("set_default_permission", request)
    
    async def _api_reload_permissions(self, request: dict):
        """
        API端点：重新加载所有权限配置到内存（仅P0级用户可用）
        """
        return self.engine.handle_request("reload_permissions", request)