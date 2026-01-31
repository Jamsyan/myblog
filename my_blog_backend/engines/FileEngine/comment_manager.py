import os
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional


class CommentManager:
    """
    评论管理类，负责评论的添加、读取和管理，实现冷热分离策略
    """
    
    def __init__(self, data_dir: str, db_manager: Any, logger: Any, queue_manager: Any):
        """
        初始化评论管理器
        
        Args:
            data_dir: 数据目录路径
            db_manager: 数据库管理器实例
            logger: 日志记录器实例
            queue_manager: 队列管理器实例
        """
        self.data_dir = data_dir
        self.db_manager = db_manager
        self.logger = logger
        self.queue_manager = queue_manager
        
        # 评论文件存储目录
        self.comments_dir = os.path.join(self.data_dir, "comments")
        self.hot_comments_dir = os.path.join(self.comments_dir, "hot")
        self.cold_comments_dir = os.path.join(self.comments_dir, "cold")
        
        # 创建目录
        os.makedirs(self.hot_comments_dir, exist_ok=True)
        os.makedirs(self.cold_comments_dir, exist_ok=True)
        
        # 冷热帖子阈值（10秒内请求数）
        self.hot_threshold = 10
        
        # 冷评论文件大小限制（100个帖子/文件）
        self.cold_file_limit = 100
        
        # 临时URL生命周期（分钟）
        self.temp_url_lifetime = 30
        
        # 请求频率统计
        self.request_stats = {}
        
    def _cleanup_expired_request_stats(self):
        """
        清理过期的请求统计数据（超过10秒的）
        """
        now = time.time()
        expired_posts = []
        
        for post_id, requests in self.request_stats.items():
            # 保留10秒内的请求
            self.request_stats[post_id] = [req for req in requests if now - req < 10]
            if not self.request_stats[post_id]:
                expired_posts.append(post_id)
        
        # 删除没有请求的帖子
        for post_id in expired_posts:
            del self.request_stats[post_id]
    
    def _check_post_heat(self, post_id: str) -> bool:
        """
        检查帖子热度，更新请求统计
        
        Args:
            post_id: 帖子ID
            
        Returns:
            bool: 是否为热帖子
        """
        now = time.time()
        
        # 清理过期统计
        self._cleanup_expired_request_stats()
        
        # 更新请求统计
        if post_id not in self.request_stats:
            self.request_stats[post_id] = []
        
        self.request_stats[post_id].append(now)
        
        # 检查请求频率
        request_count = len(self.request_stats[post_id])
        is_hot = request_count > self.hot_threshold
        
        # 更新帖子热度状态
        if is_hot:
            self.db_manager.update_post(post_id, is_hot=True)
        
        return is_hot
    
    def _get_comment_file(self, post_id: str, is_hot: bool) -> str:
        """
        获取评论文件路径
        
        Args:
            post_id: 帖子ID
            is_hot: 是否为热帖子
            
        Returns:
            str: 评论文件路径
        """
        if is_hot:
            return self._get_hot_comment_file(post_id)
        else:
            return self._get_cold_comment_file(post_id)
    
    def _get_hot_comment_file(self, post_id: str) -> str:
        """
        获取热帖子的评论文件路径
        
        Args:
            post_id: 帖子ID
            
        Returns:
            str: 评论文件路径
        """
        file_name = f"{post_id}.json"
        file_path = os.path.join(self.hot_comments_dir, file_name)
        
        if os.path.exists(file_path):
            return file_path
        
        self._create_hot_comment_file(file_path, post_id)
        return file_path
    
    def _create_hot_comment_file(self, file_path: str, post_id: str):
        """
        创建热帖子的评论文件
        
        Args:
            file_path: 文件路径
            post_id: 帖子ID
        """
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({"comments": []}, f, ensure_ascii=False, indent=2)
        self.db_manager.add_comment_file(file_path, post_id, is_hot=True)
    
    def _get_cold_comment_file(self, post_id: str) -> str:
        """
        获取冷帖子的评论文件路径
        
        Args:
            post_id: 帖子ID
            
        Returns:
            str: 评论文件路径
        """
        existing_file = self._find_existing_cold_file(post_id)
        if existing_file:
            return existing_file
        
        available_file = self._find_available_cold_file()
        if available_file:
            return available_file
        
        return self._create_new_cold_file()
    
    def _find_existing_cold_file(self, post_id: str) -> Optional[str]:
        """
        查找已存在的冷评论文件
        
        Args:
            post_id: 帖子ID
            
        Returns:
            Optional[str]: 文件路径，不存在返回None
        """
        comment_file = self.db_manager.get_comment_file_by_post(post_id)
        if comment_file:
            return comment_file["file_path"]
        return None
    
    def _find_available_cold_file(self) -> Optional[str]:
        """
        查找可用的冷评论文件（未满的）
        
        Returns:
            Optional[str]: 文件路径，没有可用文件返回None
        """
        cold_files = [f for f in os.listdir(self.cold_comments_dir) if f.endswith(".json")]
        
        for cold_file in cold_files:
            file_path = os.path.join(self.cold_comments_dir, cold_file)
            if self._is_cold_file_available(file_path):
                return file_path
        
        return None
    
    def _is_cold_file_available(self, file_path: str) -> bool:
        """
        检查冷评论文件是否可用（未满）
        
        Args:
            file_path: 文件路径
            
        Returns:
            bool: 可用返回True，否则返回False
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = json.load(f)
            return len(content) < self.cold_file_limit
        except json.JSONDecodeError:
            return False
    
    def _create_new_cold_file(self) -> str:
        """
        创建新的冷评论文件
        
        Returns:
            str: 新文件路径
        """
        file_name = f"comments_{str(uuid.uuid4())[:8]}.json"
        file_path = os.path.join(self.cold_comments_dir, file_name)
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump({}, f, ensure_ascii=False, indent=2)
        
        self.db_manager.add_comment_file(file_path, is_hot=False)
        return file_path
    
    def add_comment(self, post_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加评论
        
        Args:
            post_id: 帖子ID
            comment_data: 评论数据
            
        Returns:
            Dict[str, Any]: 添加结果
        """
        try:
            post_info = self.db_manager.get_post(post_id)
            if not post_info:
                return {
                    "error": f"Post {post_id} not found",
                    "status": "error"
                }
            
            is_hot = self._check_post_heat(post_id)
            comment_file = self._get_comment_file(post_id, is_hot)
            comment = self._build_comment(post_id, comment_data)
            
            if is_hot:
                return self._add_hot_comment(comment_file, comment)
            else:
                return self._add_cold_comment(comment_file, post_id, comment)
        except Exception as e:
            self.logger.error(f"添加评论失败: 帖子ID {post_id}, 错误: {str(e)}")
            return {
                "error": f"Failed to add comment: {str(e)}",
                "status": "error"
            }
    
    def _build_comment(self, post_id: str, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建评论数据
        
        Args:
            post_id: 帖子ID
            comment_data: 评论数据
            
        Returns:
            Dict[str, Any]: 评论数据
        """
        comment_id = str(uuid.uuid4())
        return {
            "id": comment_id,
            "post_id": post_id,
            "content": comment_data.get("content", ""),
            "author": comment_data.get("author", "anonymous"),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    
    def _add_hot_comment(self, comment_file: str, comment: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加热帖子的评论（使用队列处理）
        
        Args:
            comment_file: 评论文件路径
            comment: 评论数据
            
        Returns:
            Dict[str, Any]: 添加结果
        """
        def _add_comment_to_file():
            with open(comment_file, "r+", encoding="utf-8") as f:
                content = json.load(f)
                content["comments"].append(comment)
                f.seek(0)
                json.dump(content, f, ensure_ascii=False, indent=2)
                f.truncate()
        
        self.queue_manager.add_task(_add_comment_to_file)
        
        return {
            "comment_id": comment["id"],
            "status": "success",
            "queue_processed": True
        }
    
    def _add_cold_comment(self, comment_file: str, post_id: str, comment: Dict[str, Any]) -> Dict[str, Any]:
        """
        添加冷帖子的评论（直接处理）
        
        Args:
            comment_file: 评论文件路径
            post_id: 帖子ID
            comment: 评论数据
            
        Returns:
            Dict[str, Any]: 添加结果
        """
        with open(comment_file, "r+", encoding="utf-8") as f:
            content = json.load(f)
            
            if post_id not in content:
                content[post_id] = {"comments": []}
            
            content[post_id]["comments"].append(comment)
            
            f.seek(0)
            json.dump(content, f, ensure_ascii=False, indent=2)
            f.truncate()
        
        return {
            "comment_id": comment["id"],
            "status": "success",
            "queue_processed": False
        }
    
    def get_comments(self, post_id: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        获取帖子评论
        
        Args:
            post_id: 帖子ID
            page: 页码
            limit: 每页数量
            
        Returns:
            Dict[str, Any]: 评论数据或临时URL
        """
        try:
            # 检查帖子是否存在
            post_info = self.db_manager.get_post(post_id)
            if not post_info:
                return {
                    "error": f"Post {post_id} not found",
                    "status": "error"
                }
            
            # 检查帖子热度
            is_hot = self._check_post_heat(post_id)
            
            # 获取评论文件
            comment_file = self._get_comment_file(post_id, is_hot)
            
            # 读取评论文件
            with open(comment_file, "r", encoding="utf-8") as f:
                content = json.load(f)
            
            # 提取当前帖子的评论
            if is_hot:
                # 热帖子，评论直接在comments字段下
                post_comments = content.get("comments", [])
            else:
                # 冷帖子，评论在以post_id为key的字段下
                post_comments = content.get(post_id, {}).get("comments", [])
            
            # 排序评论（最新的在前）
            post_comments.sort(key=lambda x: x["created_at"], reverse=True)
            
            # 分页
            start = (page - 1) * limit
            end = start + limit
            paginated_comments = post_comments[start:end]
            
            total = len(post_comments)
            
            # 生成临时URL（如果需要）
            if total > limit * 5:  # 如果评论超过5页，生成临时URL
                temp_url = f"/temp/{str(uuid.uuid4())[:16]}"
                
                # 计算过期时间
                expires_at = (datetime.now() + timedelta(minutes=self.temp_url_lifetime)).isoformat()
                
                # 添加临时URL到数据库
                self.db_manager.add_temp_url(temp_url, comment_file, expires_at)
                
                return {
                    "temp_url": temp_url,
                    "page": page,
                    "limit": limit,
                    "total": total,
                    "comments": paginated_comments,
                    "status": "success"
                }
            
            return {
                "page": page,
                "limit": limit,
                "total": total,
                "comments": paginated_comments,
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"获取评论失败: 帖子ID {post_id}, 错误: {str(e)}")
            return {
                "error": f"Failed to get comments: {str(e)}",
                "status": "error"
            }
    
    def get_temp_url_content(self, temp_url: str) -> Optional[str]:
        """
        获取临时URL对应的文件路径
        
        Args:
            temp_url: 临时URL
            
        Returns:
            Optional[str]: 实际文件路径，不存在或过期返回None
        """
        # 获取临时URL信息
        temp_url_info = self.db_manager.get_temp_url(temp_url)
        if not temp_url_info:
            return None
        
        # 检查是否过期
        expires_at = datetime.fromisoformat(temp_url_info["expires_at"])
        if datetime.now() > expires_at:
            return None
        
        # 更新访问时间
        self.db_manager.update_temp_url_access(temp_url)
        
        return temp_url_info["actual_path"]
    
    def cleanup_expired_temp_urls(self) -> int:
        """
        清理过期的临时URL
        
        Returns:
            int: 删除的临时URL数量
        """
        return self.db_manager.delete_expired_temp_urls()