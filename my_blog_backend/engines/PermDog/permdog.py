from BaseEngine import BaseEngine
from typing import Dict, Any, List
import os
import sys
from datetime import datetime

# 添加当前目录到Python路径，以便直接运行脚本时能导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# 添加项目根目录到Python路径，以便导入LinkGateway模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 使用绝对导入
from database import DatabaseManager
from permission_manager import PermissionManager
from api_routes import APIRoutes
from LinkGateway.logs import get_logger
from LinkGateway.standards import APIStandard


class PermDogEngine(BaseEngine):
    """
    权限引擎，用于管理系统权限体系
    """
    
    def __init__(self, service_name: str, version: str, engine_type: str = "kernel"):
        """
        初始化权限引擎
        
        Args:
            service_name: 服务名称
            version: 服务版本
            engine_type: 引擎类型，kernel表示内核引擎，network表示网络引擎
        """
        super().__init__(service_name, version, engine_type)
        
        # 初始化日志记录器
        self.logger = get_logger(service_name)
        
        # 使用BaseEngine提供的统一方法获取数据目录和数据库路径
        self.data_dir = self.get_data_dir()
        self.db_path = self.get_db_path()
        
        # 初始化数据库管理器
        self.db_manager = DatabaseManager(self.db_path)
        
        # 初始化权限管理器
        self.permission_manager = PermissionManager(self.data_dir, self.db_manager, self.logger)
        
        # 初始化API路由
        self.api_routes = APIRoutes(self)
        
        self.logger.info(f"{service_name} 引擎初始化成功")
    
    def start(self) -> bool:
        """
        启动引擎
        
        Returns:
            bool: 启动成功返回True，失败返回False
        """
        # 初始化默认权限配置到数据库
        self.logger.info("开始初始化默认权限配置")
        self.permission_manager.init_default_permissions()
        
        # 预加载所有权限配置到内存
        self.permission_manager._preload_permissions()
        
        self.status = "running"
        self.logger.info(f"PermDogEngine '{self.service_name}' started successfully")
        return True
    
    def stop(self) -> bool:
        """
        停止引擎
        
        Returns:
            bool: 停止成功返回True，失败返回False
        """
        self.status = "stopped"
        self.logger.info(f"PermDogEngine '{self.service_name}' stopped successfully")
        return True
    
    def _handle_request_impl(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        实际的请求处理逻辑（子类实现）
        
        Args:
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        self.logger.debug(f"处理请求: {action}, 数据: {data}")
        
        action_handlers = {
            "register_operation": lambda: self.permission_manager.register_operation(
                data.get("operation_name"),
                data.get("description", "")
            ),
            "register_component": lambda: self.permission_manager.register_component(
                data.get("component_id"),
                data.get("component_name"),
                data.get("description", "")
            ),
            "get_default_permission": lambda: self.permission_manager.get_default_permission(),
            "check_operation_permission": lambda: self.permission_manager.check_operation_permission(
                data.get("permission_level"),
                data.get("operation_name")
            ),
            "check_component_permission": lambda: self.permission_manager.check_component_permission(
                data.get("permission_level"),
                data.get("component_id")
            ),
            "get_permission_config": lambda: self._handle_get_permission_config(data),
            "update_permission_config": lambda: self.permission_manager.update_permission_config(
                data.get("permission_level"),
                data.get("allowed_operations", []),
                data.get("allowed_components", [])
            ),
            "set_default_permission": lambda: self._handle_set_default_permission(data),
            "reload_permissions": lambda: self._handle_reload_permissions(data)
        }
        
        handler = action_handlers.get(action)
        if handler:
            return handler()
        
        self.logger.error(f"未知请求动作: {action}")
        return {
            "error": f"Unknown action: {action}",
            "status": "error"
        }
    
    def _handle_get_permission_config(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理获取权限配置请求
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        permission_level = data.get("permission_level")
        if not permission_level:
            return {
                "error": "Missing 'permission_level' field",
                "status": "error"
            }
        
        config = self.permission_manager.load_permission_config(permission_level)
        if config:
            return {
                "config": config,
                "status": "success"
            }
        
        return {
            "error": f"Permission level '{permission_level}' not found",
            "status": "error"
        }
    
    def _handle_set_default_permission(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理设置默认权限请求
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        permission_level = data.get("permission_level")
        if not permission_level:
            return {
                "error": "Missing 'permission_level' field",
                "status": "error"
            }
        
        success = self.permission_manager.set_default_permission(permission_level)
        if success:
            return {
                "message": f"Default permission level set to '{permission_level}'",
                "status": "success"
            }
        
        return {
            "error": f"Failed to set default permission level to '{permission_level}'",
            "status": "error"
        }
    
    def _handle_reload_permissions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理权限热更新请求
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        user_permission_level = data.get("user_permission_level")
        if not user_permission_level:
            return {
                "error": "Missing 'user_permission_level' field",
                "status": "error"
            }
        
        if user_permission_level != "p0":
            self.logger.warning(f"权限不足: 用户权限等级 {user_permission_level} 试图调用热更新接口")
            return {
                "error": "Permission denied: Only P0 users can reload permissions",
                "status": "error"
            }
        
        success = self.permission_manager.reload_permissions()
        if success:
            return {
                "message": "Permissions reloaded successfully",
                "status": "success"
            }
        
        return {
            "error": "Failed to reload permissions",
            "status": "error"
        }
    
    def get_api_routes(self) -> List[Dict[str, Any]]:
        """
        获取引擎的API路由定义
        
        Returns:
            List[Dict[str, Any]]: API路由定义列表
        """
        return self.api_routes.get_api_routes()
    
    def get_formatted_api_routes(self) -> List[Dict[str, Any]]:
        """
        获取格式化后的API路由定义，确保符合LinkGateway标准
        
        Returns:
            List[Dict[str, Any]]: 格式化后的API路由定义列表
        """
        try:
            api_routes = self.get_api_routes()
            formatted_routes = []
            
            for route in api_routes:
                # 标准化HTTP方法
                method = APIStandard.normalize_api_method(route.get("method"))
                # 格式化API路径
                path = APIStandard.format_api_path("engine", "permdog", route.get("path"))
                
                formatted_route = {
                    "path": path,
                    "method": method,
                    "description": route.get("description", ""),
                    "handler": route.get("handler")
                }
                formatted_routes.append(formatted_route)
            
            return formatted_routes
        except Exception as e:
            self.logger.error(f"格式化API路由失败: {str(e)}")
            return []
    
    def get_dependencies(self) -> List[str]:
        """
        获取引擎依赖的其他服务
        
        Returns:
            List[str]: 依赖服务列表
        """
        return []
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        return {
            "status": "healthy",
            "service_id": self.service_id,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取引擎元数据
        
        Returns:
            Dict[str, Any]: 引擎元数据
        """
        return {
            "service_id": self.service_id,
            "service_name": self.service_name,
            "version": self.version,
            "engine_type": self.engine_type,
            "status": self.status
        }