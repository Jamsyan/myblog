from typing import Dict, Any, List
import sys
import os

# 添加当前目录到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 添加项目根目录到sys.path，以便导入LinkGateway模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import PostService
from api import setup_router
from LinkGateway.logs import get_logger
from LinkGateway.standards import APIStandard

# 使用LinkGateway提供的日志模块
logger = get_logger("post-service")


class PostServerService:
    """
    帖子服务器业务逻辑类，负责处理帖子相关的核心业务逻辑
    """
    
    def __init__(self, db_path: str, linkgateway_url: str = "http://localhost:8000"):
        """
        初始化帖子服务器
        
        Args:
            db_path: 数据库路径
            linkgateway_url: LinkGateway的访问地址
        """
        self.db_path = db_path
        self.linkgateway_url = linkgateway_url
        self.post_service = PostService(db_path, linkgateway_url)
        self.logger = logger
        
        self.logger.info("帖子管理服务初始化成功")
    
    def start(self) -> bool:
        """
        启动帖子服务器
        
        Returns:
            bool: 启动成功返回True，失败返回False
        """
        try:
            self.logger.info("帖子管理服务启动成功")
            return True
        except Exception as e:
            self.logger.error(f"帖子管理服务启动失败: {str(e)}")
            return False
    
    def stop(self) -> bool:
        """
        停止帖子服务器
        
        Returns:
            bool: 停止成功返回True，失败返回False
        """
        try:
            self.post_service.close()
            self.logger.info("帖子管理服务停止成功")
            return True
        except Exception as e:
            self.logger.error(f"帖子管理服务停止失败: {str(e)}")
            return False
    
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        from datetime import datetime
        return {
            "status": "healthy",
            "service_id": "post-service",
            "service_name": "帖子管理服务",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_api_routes(self) -> List[Dict[str, Any]]:
        """
        获取API路由定义
        
        Returns:
            List[Dict[str, Any]]: API路由定义列表
        """
        # 从service.json文件中读取API定义
        import json
        import os
        current_path = os.path.abspath(__file__)
        service_json_path = os.path.join(os.path.dirname(current_path), "service.json")
        
        try:
            with open(service_json_path, "r", encoding="utf-8") as f:
                service_info = json.load(f)
            return service_info.get("apis", [])
        except Exception as e:
            self.logger.error(f"读取service.json文件失败: {str(e)}")
            return []
    
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
                path = APIStandard.format_api_path("business", "post-service", route.get("path"))
                
                formatted_route = {
                    "path": path,
                    "method": method,
                    "description": route.get("description", "")
                }
                formatted_routes.append(formatted_route)
            
            return formatted_routes
        except Exception as e:
            self.logger.error(f"格式化API路由失败: {str(e)}")
            return []
