import os
import uuid
from datetime import datetime
from typing import Dict, Any, Optional


class PostManager:
    """
    帖子管理类，负责帖子的创建、读取、更新和删除
    """
    
    def __init__(self, data_dir: str, db_manager: Any, logger: Any):
        """
        初始化帖子管理器
        
        Args:
            data_dir: 数据目录路径
            db_manager: 数据库管理器实例
            logger: 日志记录器实例
        """
        self.data_dir = data_dir
        self.db_manager = db_manager
        self.logger = logger
        
        # 帖子文件存储目录
        self.posts_dir = os.path.join(self.data_dir, "posts")
        os.makedirs(self.posts_dir, exist_ok=True)
    
    def analyze_post_content(self, post_content: str) -> str:
        """
        分析帖子内容，判断是否包含视频，返回合适的文件类型
        
        Args:
            post_content: 帖子内容
            
        Returns:
            str: 文件类型，"md"或"html"
        """
        # 检查是否包含视频标签
        if "<video" in post_content.lower() or "</video>" in post_content.lower():
            return "html"
        return "md"
    
    def create_post(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        创建帖子
        
        Args:
            post_data: 帖子数据，包含title和content
            
        Returns:
            Dict[str, Any]: 包含帖子ID和文件路径的结果
        """
        try:
            # 生成帖子ID
            post_id = str(uuid.uuid4())
            title = post_data.get("title", "")
            content = post_data.get("content", "")
            
            if not title or not content:
                return {
                    "error": "Missing title or content",
                    "status": "error"
                }
            
            # 分析帖子内容，选择文件类型
            file_type = self.analyze_post_content(content)
            
            # 创建帖子文件路径
            file_name = f"{post_id}.{file_type}"
            file_path = os.path.join(self.posts_dir, file_name)
            
            # 写入帖子内容
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # 获取权限相关字段
            permission_level = post_data.get("permission_level", "p0")
            created_by = post_data.get("created_by")
            is_public = post_data.get("is_public", True)
            
            # 将帖子信息存储到数据库
            success = self.db_manager.add_post(
                post_id, title, file_path, file_type,
                permission_level=permission_level,
                created_by=created_by,
                is_public=is_public
            )
            if not success:
                # 数据库添加失败，删除已创建的文件
                os.remove(file_path)
                return {
                    "error": "Failed to add post to database",
                    "status": "error"
                }
            
            self.logger.debug(f"创建帖子成功: {post_id}, 文件路径: {file_path}")
            
            return {
                "post_id": post_id,
                "file_path": file_path,
                "file_type": file_type,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"创建帖子失败: {str(e)}")
            return {
                "error": f"Failed to create post: {str(e)}",
                "status": "error"
            }
    
    def get_post(self, post_id: str) -> Dict[str, Any]:
        """
        获取帖子
        
        Args:
            post_id: 帖子ID
            
        Returns:
            Dict[str, Any]: 包含帖子信息和文件路径的结果
        """
        try:
            # 从数据库获取帖子信息
            post_info = self.db_manager.get_post(post_id)
            if not post_info:
                return {
                    "error": f"Post {post_id} not found",
                    "status": "error"
                }
            
            # 检查文件是否存在
            file_path = post_info["file_path"]
            if not os.path.exists(file_path):
                return {
                    "error": f"Post file {file_path} not found",
                    "status": "error"
                }
            
            # 读取帖子内容
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            return {
                "post_id": post_id,
                "title": post_info["title"],
                "content": content,
                "file_path": file_path,
                "file_type": post_info["file_type"],
                "permission_level": post_info["permission_level"],
                "created_by": post_info["created_by"],
                "is_public": bool(post_info["is_public"]),
                "created_at": post_info["created_at"],
                "updated_at": post_info["updated_at"],
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"获取帖子失败: {post_id}, 错误: {str(e)}")
            return {
                "error": f"Failed to get post: {str(e)}",
                "status": "error"
            }
    
    def update_post(self, post_id: str, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        更新帖子
        
        Args:
            post_id: 帖子ID
            post_data: 更新后的帖子数据，包含title和content
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        try:
            post_info = self.db_manager.get_post(post_id)
            if not post_info:
                return {
                    "error": f"Post {post_id} not found",
                    "status": "error"
                }
            
            content = post_data.get("content", None)
            
            if content is None:
                return self._update_post_metadata(post_id, post_info, post_data)
            
            return self._update_post_with_content(post_id, post_info, post_data, content)
        except Exception as e:
            self.logger.error(f"更新帖子失败: {post_id}, 错误: {str(e)}")
            return {
                "error": f"Failed to update post: {str(e)}",
                "status": "error"
            }
    
    def _update_post_metadata(self, post_id: str, post_info: Dict[str, Any], post_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        只更新帖子的元数据（标题、权限等）
        
        Args:
            post_id: 帖子ID
            post_info: 帖子信息
            post_data: 更新数据
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        title = post_data.get("title", post_info["title"])
        permission_level = post_data.get("permission_level")
        created_by = post_data.get("created_by")
        is_public = post_data.get("is_public")
        
        success = self.db_manager.update_post(
            post_id, 
            title=title,
            permission_level=permission_level,
            created_by=created_by,
            is_public=is_public
        )
        
        if success:
            self.logger.debug(f"更新帖子标题成功: {post_id}")
            return {
                "post_id": post_id,
                "status": "success"
            }
        
        return {
            "error": "Failed to update post title in database",
            "status": "error"
        }
    
    def _update_post_with_content(self, post_id: str, post_info: Dict[str, Any], post_data: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        更新帖子内容
        
        Args:
            post_id: 帖子ID
            post_info: 帖子信息
            post_data: 更新数据
            content: 新内容
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        new_file_type = self.analyze_post_content(content)
        old_file_type = post_info["file_type"]
        
        if new_file_type != old_file_type:
            return self._update_post_with_new_file_type(post_id, post_info, post_data, content, new_file_type)
        
        return self._update_post_same_file_type(post_id, post_info, post_data, content)
    
    def _update_post_with_new_file_type(self, post_id: str, post_info: Dict[str, Any], post_data: Dict[str, Any], content: str, new_file_type: str) -> Dict[str, Any]:
        """
        更新帖子，文件类型改变
        
        Args:
            post_id: 帖子ID
            post_info: 帖子信息
            post_data: 更新数据
            content: 新内容
            new_file_type: 新文件类型
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        old_file_path = post_info["file_path"]
        new_file_name = f"{post_id}.{new_file_type}"
        new_file_path = os.path.join(self.posts_dir, new_file_name)
        
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        title = post_data.get("title", post_info["title"])
        permission_level = post_data.get("permission_level")
        created_by = post_data.get("created_by")
        is_public = post_data.get("is_public")
        
        success = self.db_manager.update_post(
            post_id, 
            title=title, 
            file_path=new_file_path, 
            file_type=new_file_type,
            permission_level=permission_level,
            created_by=created_by,
            is_public=is_public
        )
        
        if success:
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            self.logger.debug(f"更新帖子并更改文件类型成功: {post_id}")
            return {
                "post_id": post_id,
                "file_path": new_file_path,
                "file_type": new_file_type,
                "status": "success"
            }
        
        os.remove(new_file_path)
        return {
            "error": "Failed to update post in database",
            "status": "error"
        }
    
    def _update_post_same_file_type(self, post_id: str, post_info: Dict[str, Any], post_data: Dict[str, Any], content: str) -> Dict[str, Any]:
        """
        更新帖子，文件类型不变
        
        Args:
            post_id: 帖子ID
            post_info: 帖子信息
            post_data: 更新数据
            content: 新内容
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        old_file_path = post_info["file_path"]
        old_file_type = post_info["file_type"]
        
        with open(old_file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        title = post_data.get("title", post_info["title"])
        permission_level = post_data.get("permission_level")
        created_by = post_data.get("created_by")
        is_public = post_data.get("is_public")
        
        success = self.db_manager.update_post(
            post_id, 
            title=title,
            permission_level=permission_level,
            created_by=created_by,
            is_public=is_public
        )
        
        if success:
            self.logger.debug(f"更新帖子成功: {post_id}")
            return {
                "post_id": post_id,
                "file_path": old_file_path,
                "file_type": old_file_type,
                "status": "success"
            }
        
        return {
            "error": "Failed to update post in database",
            "status": "error"
        }
    
    def delete_post(self, post_id: str) -> Dict[str, Any]:
        """
        删除帖子
        
        Args:
            post_id: 帖子ID
            
        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            # 从数据库获取帖子信息
            post_info = self.db_manager.get_post(post_id)
            if not post_info:
                return {
                    "error": f"Post {post_id} not found",
                    "status": "error"
                }
            
            # 删除帖子文件
            file_path = post_info["file_path"]
            if os.path.exists(file_path):
                os.remove(file_path)
            
            # 从数据库删除帖子
            success = self.db_manager.delete_post(post_id)
            if success:
                self.logger.debug(f"删除帖子成功: {post_id}")
                return {
                    "post_id": post_id,
                    "status": "success"
                }
            else:
                return {
                    "error": "Failed to delete post from database",
                    "status": "error"
                }
        except Exception as e:
            self.logger.error(f"删除帖子失败: {post_id}, 错误: {str(e)}")
            return {
                "error": f"Failed to delete post: {str(e)}",
                "status": "error"
            }
    
    def get_post_file_path(self, post_id: str) -> Optional[str]:
        """
        获取帖子文件路径
        
        Args:
            post_id: 帖子ID
            
        Returns:
            Optional[str]: 帖子文件路径，不存在返回None
        """
        post_info = self.db_manager.get_post(post_id)
        if post_info and os.path.exists(post_info["file_path"]):
            return post_info["file_path"]
        return None