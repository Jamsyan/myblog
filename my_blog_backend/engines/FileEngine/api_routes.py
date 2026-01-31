from typing import Dict, Any, List


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
                "path": "/health",
                "methods": ["GET"],
                "endpoint": self._api_health_check,
                "description": "健康检查接口"
            },
            {
                "path": "/create_post",
                "methods": ["POST"],
                "endpoint": self._api_create_post,
                "description": "创建帖子接口"
            },
            {
                "path": "/get_post",
                "methods": ["GET"],
                "endpoint": self._api_get_post,
                "description": "获取帖子接口"
            },
            {
                "path": "/update_post",
                "methods": ["PUT"],
                "endpoint": self._api_update_post,
                "description": "更新帖子接口"
            },
            {
                "path": "/delete_post",
                "methods": ["DELETE"],
                "endpoint": self._api_delete_post,
                "description": "删除帖子接口"
            },
            {
                "path": "/add_comment",
                "methods": ["POST"],
                "endpoint": self._api_add_comment,
                "description": "添加评论接口"
            },
            {
                "path": "/get_comments",
                "methods": ["GET"],
                "endpoint": self._api_get_comments,
                "description": "获取评论接口"
            }
        ]
    
    # API端点方法
    async def _api_health_check(self, request: dict):
        """
        API端点：健康检查
        """
        return self.engine.health_check()
    
    async def _api_create_post(self, request: dict):
        """
        API端点：创建帖子
        """
        return self.engine.handle_request("create_post", request)
    
    async def _api_get_post(self, request: dict):
        """
        API端点：获取帖子
        """
        return self.engine.handle_request("get_post", request)
    
    async def _api_update_post(self, request: dict):
        """
        API端点：更新帖子
        """
        return self.engine.handle_request("update_post", request)
    
    async def _api_delete_post(self, request: dict):
        """
        API端点：删除帖子
        """
        return self.engine.handle_request("delete_post", request)
    
    async def _api_add_comment(self, request: dict):
        """
        API端点：添加评论
        """
        return self.engine.handle_request("add_comment", request)
    
    async def _api_get_comments(self, request: dict):
        """
        API端点：获取评论
        """
        return self.engine.handle_request("get_comments", request)