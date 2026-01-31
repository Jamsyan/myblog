from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import requests
import os
import sys

# 添加当前目录到sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 使用LinkGateway提供的日志模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from LinkGateway.logs import get_logger
logger = get_logger("interaction-service")

# 动态导入数据库操作，避免模块导入冲突
def _get_interaction_database():
    import sys
    import os
    import importlib.util
    
    # 获取当前文件的目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 构建database.py文件的绝对路径
    database_path = os.path.join(current_dir, "database.py")
    
    # 使用绝对路径创建模块规范
    spec = importlib.util.spec_from_file_location('database', database_path)
    if spec and spec.loader:
        # 创建模块并执行
        database_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(database_module)
        return database_module.InteractionDatabase
    else:
        raise ImportError(f"Failed to import database module from {database_path}")

InteractionDatabase = _get_interaction_database()

class InteractionService:
    """
    互动服务核心业务逻辑类，负责处理点赞和评论功能
    """
    
    def __init__(self, db_path: str, linkgateway_url: str = "http://localhost:8000"):
        """
        初始化互动服务
        
        Args:
            db_path: 数据库文件路径
            linkgateway_url: LinkGateway的访问地址
        """
        self.db_path = db_path
        self.linkgateway_url = linkgateway_url
        self.db_manager = InteractionDatabase(db_path)
        logger.info("互动服务初始化成功")
    
    def _call_file_engine(self, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        通过LinkGateway服务代理调用FileEngine引擎
        
        Args:
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 请求结果
        """
        try:
            url = f"{self.linkgateway_url}/internal/proxy/fileengine"
            payload = {
                "action": action,
                "data": data or {}
            }
            
            logger.info(f"调用FileEngine: 动作={action}, 数据={data}")
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"FileEngine响应: {result}")
                return result
            else:
                logger.error(f"调用FileEngine失败: {response.status_code}, {response.text}")
                return {"error": f"调用FileEngine失败: {response.status_code}"}
        except Exception as e:
            logger.error(f"调用FileEngine时发生异常: {str(e)}")
            return {"error": str(e)}
    
    def like_post(self, db: Session, user_id: int, post_id: str) -> Dict[str, Any]:
        """
        点赞帖子
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            post_id: 帖子ID
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            if self.db_manager.is_liked(db, user_id, post_id):
                return self._get_like_error_result("您已经点赞过该帖子", db, post_id)
            
            return self._add_like(db, user_id, post_id)
        except Exception as e:
            logger.error(f"点赞帖子失败: {str(e)}")
            return self._get_like_error_result(f"点赞失败: {str(e)}", db, post_id)
    
    def _get_like_error_result(self, message: str, db: Session, post_id: str) -> Dict[str, Any]:
        """
        获取点赞错误结果
        
        Args:
            message: 错误消息
            db: 数据库会话
            post_id: 帖子ID
            
        Returns:
            Dict[str, Any]: 错误结果
        """
        return {
            "status": "error",
            "message": message,
            "like_count": self.db_manager.get_like_count(db, post_id)
        }
    
    def _add_like(self, db: Session, user_id: int, post_id: str) -> Dict[str, Any]:
        """
        添加点赞
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            post_id: 帖子ID
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        if not self.db_manager.add_like(db, user_id, post_id):
            return self._get_like_error_result("添加点赞记录失败", db, post_id)
        
        new_like_count = self.db_manager.update_like_count(db, post_id, increment=1)
        if new_like_count is not None:
            return {
                "status": "success",
                "message": "点赞成功",
                "like_count": new_like_count
            }
        
        self.db_manager.remove_like(db, user_id, post_id)
        return self._get_like_error_result("更新点赞数失败", db, post_id)
    
    def unlike_post(self, db: Session, user_id: int, post_id: str) -> Dict[str, Any]:
        """
        取消点赞帖子
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            post_id: 帖子ID
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            if not self.db_manager.is_liked(db, user_id, post_id):
                return self._get_like_error_result("您还没有点赞过该帖子", db, post_id)
            
            return self._remove_like(db, user_id, post_id)
        except Exception as e:
            logger.error(f"取消点赞帖子失败: {str(e)}")
            return self._get_like_error_result(f"取消点赞失败: {str(e)}", db, post_id)
    
    def _remove_like(self, db: Session, user_id: int, post_id: str) -> Dict[str, Any]:
        """
        移除点赞
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            post_id: 帖子ID
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        if not self.db_manager.remove_like(db, user_id, post_id):
            return self._get_like_error_result("移除点赞记录失败", db, post_id)
        
        new_like_count = self.db_manager.update_like_count(db, post_id, increment=-1)
        if new_like_count is not None:
            return {
                "status": "success",
                "message": "取消点赞成功",
                "like_count": new_like_count
            }
        
        self.db_manager.add_like(db, user_id, post_id)
        return self._get_like_error_result("更新点赞数失败", db, post_id)
    
    def get_post_likes(self, db: Session, post_id: str) -> Dict[str, Any]:
        """
        获取帖子点赞数
        
        Args:
            db: 数据库会话
            post_id: 帖子ID
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            like_count = self.db_manager.get_like_count(db, post_id)
            return {
                "status": "success",
                "like_count": like_count
            }
        except Exception as e:
            logger.error(f"获取帖子点赞数失败: {str(e)}")
            return {
                "status": "error",
                "message": f"获取点赞数失败: {str(e)}",
                "like_count": 0
            }
    
    def get_user_likes(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        获取用户点赞记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过的记录数
            limit: 返回的记录数
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            likes = self.db_manager.get_user_likes(db, user_id, skip, limit)
            return {
                "status": "success",
                "likes": likes,
                "total": len(likes)
            }
        except Exception as e:
            logger.error(f"获取用户点赞记录失败: {str(e)}")
            return {
                "status": "error",
                "message": f"获取点赞记录失败: {str(e)}",
                "likes": [],
                "total": 0
            }
    
    def add_comment(self, post_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加评论
        
        Args:
            post_id: 帖子ID
            comment_data: 评论数据，包含content, author等字段
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            # 调用FileEngine的add_comment方法
            result = self._call_file_engine("add_comment", {
                "post_id": post_id,
                "comment_data": comment_data
            })
            
            if "error" in result:
                logger.error(f"添加评论失败: {result['error']}")
                return {
                    "status": "error",
                    "message": f"添加评论失败: {result['error']}"
                }
            
            return {
                "status": "success",
                "message": "评论添加成功",
                "comment_id": result.get("comment_id")
            }
        except Exception as e:
            logger.error(f"添加评论失败: {str(e)}")
            return {
                "status": "error",
                "message": f"添加评论失败: {str(e)}"
            }
    
    def get_comments(self, post_id: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        获取帖子评论
        
        Args:
            post_id: 帖子ID
            page: 页码
            limit: 每页数量
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            # 调用FileEngine的get_comments方法
            result = self._call_file_engine("get_comments", {
                "post_id": post_id,
                "page": page,
                "limit": limit
            })
            
            if "error" in result:
                logger.error(f"获取评论失败: {result['error']}")
                return {
                    "status": "error",
                    "message": f"获取评论失败: {result['error']}",
                    "comments": []
                }
            
            return {
                "status": "success",
                "comments": result.get("comments", []),
                "total": result.get("total", 0),
                "page": result.get("page", page),
                "limit": result.get("limit", limit)
            }
        except Exception as e:
            logger.error(f"获取评论失败: {str(e)}")
            return {
                "status": "error",
                "message": f"获取评论失败: {str(e)}",
                "comments": []
            }
    
    def delete_comment(self, comment_id: str) -> Dict[str, Any]:
        """
        删除评论
        
        Args:
            comment_id: 评论ID
            
        Returns:
            Dict[str, Any]: 操作结果
        """
        try:
            # 调用FileEngine的delete_comment方法
            result = self._call_file_engine("delete_comment", {
                "comment_id": comment_id
            })
            
            if "error" in result:
                logger.error(f"删除评论失败: {result['error']}")
                return {
                    "status": "error",
                    "message": f"删除评论失败: {result['error']}"
                }
            
            return {
                "status": "success",
                "message": "评论删除成功"
            }
        except Exception as e:
            logger.error(f"删除评论失败: {str(e)}")
            return {
                "status": "error",
                "message": f"删除评论失败: {str(e)}"
            }