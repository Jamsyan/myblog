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
from post_manager import PostManager
from comment_manager import CommentManager
from queue_manager import QueueManager
from api_routes import APIRoutes
from LinkGateway.logs import get_logger
from LinkGateway.standards import APIStandard


class FileEngine(BaseEngine):
    """
    文件处理引擎，用于处理帖子和评论的文件存储与管理
    """
    
    def __init__(self, service_name: str, version: str, engine_type: str = "kernel"):
        """
        初始化文件处理引擎
        
        Args:
            service_name: 服务名称
            version: 服务版本
            engine_type: 引擎类型，kernel表示内核引擎，network表示网络引擎
        """
        # 确保服务名称为FileEngine
        service_name = "FileEngine"
        super().__init__(service_name, version, engine_type)
        
        # 初始化日志记录器
        self.logger = get_logger(service_name)
        
        # 使用BaseEngine提供的统一方法获取数据目录和数据库路径
        self.data_dir = self.get_data_dir()
        self.db_path = self.get_db_path()
        
        # 初始化数据库管理器
        self.db_manager = DatabaseManager(self.db_path)
        
        # 初始化队列管理器
        self.queue_manager = QueueManager(max_workers=10, logger=self.logger)
        
        # 初始化帖子管理器
        self.post_manager = PostManager(self.data_dir, self.db_manager, self.logger)
        
        # 初始化评论管理器
        self.comment_manager = CommentManager(self.data_dir, self.db_manager, self.logger, self.queue_manager)
        
        # 初始化API路由
        self.api_routes = APIRoutes(self)
        
        self.logger.log_success(f"{service_name} 引擎初始化成功")
    
    def start(self) -> bool:
        """
        启动引擎
        
        Returns:
            bool: 启动成功返回True，失败返回False
        """
        # 启动队列管理器
        self.queue_manager.start()
        
        self.status = "running"
        self.logger.log_success(f"FileEngine '{self.service_name}' 启动成功")
        return True
    
    def stop(self) -> bool:
        """
        停止引擎
        
        Returns:
            bool: 停止成功返回True，失败返回False
        """
        # 停止队列管理器
        self.queue_manager.stop()
        
        self.status = "stopped"
        self.logger.log_success(f"FileEngine '{self.service_name}' 停止成功")
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
            "create_post": lambda: self.post_manager.create_post(data),
            "get_post": lambda: self._handle_get_post(data),
            "update_post": lambda: self._handle_update_post(data),
            "delete_post": lambda: self._handle_delete_post(data),
            "add_comment": lambda: self._handle_add_comment(data),
            "get_comments": lambda: self._handle_get_comments(data)
        }
        
        handler = action_handlers.get(action)
        if handler:
            return handler()
        
        self.logger.error(f"未知请求动作: {action}")
        return {
            "error": f"Unknown action: {action}",
            "status": "error"
        }
    
    def _validate_post_id(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证post_id是否存在
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 验证结果，失败返回错误字典
        """
        post_id = data.get("post_id")
        if not post_id:
            return {
                "error": "Missing post_id",
                "status": "error"
            }
        return {}
    
    def _handle_get_post(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理获取帖子请求
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        validation_error = self._validate_post_id(data)
        if validation_error:
            return validation_error
        
        return self.post_manager.get_post(data["post_id"])
    
    def _handle_update_post(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理更新帖子请求
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        validation_error = self._validate_post_id(data)
        if validation_error:
            return validation_error
        
        return self.post_manager.update_post(data["post_id"], data)
    
    def _handle_delete_post(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理删除帖子请求
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        validation_error = self._validate_post_id(data)
        if validation_error:
            return validation_error
        
        return self.post_manager.delete_post(data["post_id"])
    
    def _handle_add_comment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理添加评论请求
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        validation_error = self._validate_post_id(data)
        if validation_error:
            return validation_error
        
        return self.comment_manager.add_comment(data["post_id"], data)
    
    def _handle_get_comments(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理获取评论请求
        
        Args:
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        validation_error = self._validate_post_id(data)
        if validation_error:
            return validation_error
        
        page = data.get("page", 1)
        limit = data.get("limit", 20)
        return self.comment_manager.get_comments(data["post_id"], page, limit)
    
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
                path = APIStandard.format_api_path("engine", "FileEngine", route.get("path"))
                
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
            "service_name": self.service_name,
            "version": self.version,
            "engine_type": self.engine_type,
            "timestamp": datetime.now().isoformat()
        }