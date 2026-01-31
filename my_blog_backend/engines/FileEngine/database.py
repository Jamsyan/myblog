import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List, Optional


class DatabaseManager:
    """
    数据库管理类，负责处理数据库连接和CRUD操作
    """
    
    def __init__(self, db_path: str):
        """
        初始化数据库管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """
        初始化数据库，创建表结构
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建帖子表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            is_hot INTEGER NOT NULL DEFAULT 0,
            permission_level TEXT DEFAULT 'p0',
            created_by TEXT,
            is_public INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # 创建评论文件表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS comment_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT NOT NULL,
            post_id TEXT,
            is_hot INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id)
        )
        ''')
        
        # 创建临时URL表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS temp_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            temp_url TEXT NOT NULL UNIQUE,
            actual_path TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            accessed_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """
        执行查询操作
        
        Args:
            query: SQL查询语句
            params: 查询参数
            
        Returns:
            List[Dict[str, Any]]: 查询结果列表
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        conn.close()
        
        # 转换为字典列表
        return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """
        执行更新操作（INSERT, UPDATE, DELETE）
        
        Args:
            query: SQL更新语句
            params: 更新参数
            
        Returns:
            int: 受影响的行数
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()
        
        return affected_rows
    
    # 帖子相关操作
    def add_post(self, post_id: str, title: str, file_path: str, file_type: str, 
                 permission_level: str = 'p0', created_by: str = None, 
                 is_public: bool = True) -> bool:
        """
        添加帖子
        
        Args:
            post_id: 帖子ID
            title: 帖子标题
            file_path: 帖子文件路径
            file_type: 帖子文件类型（md或html）
            permission_level: 权限等级，关联PermDog的权限等级
            created_by: 创建者ID
            is_public: 是否公开（True：公开，False：私有）
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        query = '''
        INSERT INTO posts (id, title, file_path, file_type, is_hot, permission_level, 
                          created_by, is_public, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        params = (post_id, title, file_path, file_type, 0, permission_level, 
                 created_by, 1 if is_public else 0, now, now)
        
        try:
            self.execute_update(query, params)
            return True
        except sqlite3.IntegrityError:
            return False
    
    def update_post(self, post_id: str, title: str = None, file_path: str = None, file_type: str = None, 
                   is_hot: bool = None, permission_level: str = None, created_by: str = None, 
                   is_public: bool = None) -> bool:
        """
        更新帖子
        
        Args:
            post_id: 帖子ID
            title: 帖子标题（可选）
            file_path: 帖子文件路径（可选）
            file_type: 帖子文件类型（可选）
            is_hot: 是否为热帖子（可选）
            permission_level: 权限等级，关联PermDog的权限等级（可选）
            created_by: 创建者ID（可选）
            is_public: 是否公开（可选）
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        
        # 构建更新语句和参数
        update_fields = []
        update_params = []
        
        if title:
            update_fields.append("title = ?")
            update_params.append(title)
        if file_path:
            update_fields.append("file_path = ?")
            update_params.append(file_path)
        if file_type:
            update_fields.append("file_type = ?")
            update_params.append(file_type)
        if is_hot is not None:
            update_fields.append("is_hot = ?")
            update_params.append(1 if is_hot else 0)
        if permission_level:
            update_fields.append("permission_level = ?")
            update_params.append(permission_level)
        if created_by is not None:
            update_fields.append("created_by = ?")
            update_params.append(created_by)
        if is_public is not None:
            update_fields.append("is_public = ?")
            update_params.append(1 if is_public else 0)
        
        if not update_fields:
            return False
        
        update_fields.append("updated_at = ?")
        update_params.append(now)
        update_params.append(post_id)
        
        query = f'''UPDATE posts SET {', '.join(update_fields)} WHERE id = ?''' 
        
        affected_rows = self.execute_update(query, tuple(update_params))
        return affected_rows > 0
    
    def get_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定帖子
        
        Args:
            post_id: 帖子ID
            
        Returns:
            Optional[Dict[str, Any]]: 帖子信息，不存在返回None
        """
        query = "SELECT * FROM posts WHERE id = ?"
        params = (post_id,)
        
        result = self.execute_query(query, params)
        return result[0] if result else None
    
    def delete_post(self, post_id: str) -> bool:
        """
        删除帖子
        
        Args:
            post_id: 帖子ID
            
        Returns:
            bool: 删除成功返回True，失败返回False
        """
        query = "DELETE FROM posts WHERE id = ?"
        params = (post_id,)
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    # 评论文件相关操作
    def add_comment_file(self, file_path: str, post_id: str = None, is_hot: bool = False) -> bool:
        """
        添加评论文件
        
        Args:
            file_path: 评论文件路径
            post_id: 帖子ID（热帖子时非空）
            is_hot: 是否为热帖子评论文件
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        query = '''
        INSERT INTO comment_files (file_path, post_id, is_hot, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        '''
        params = (file_path, post_id, 1 if is_hot else 0, now, now)
        
        try:
            self.execute_update(query, params)
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_comment_file_by_post(self, post_id: str) -> Optional[Dict[str, Any]]:
        """
        根据帖子ID获取评论文件
        
        Args:
            post_id: 帖子ID
            
        Returns:
            Optional[Dict[str, Any]]: 评论文件信息，不存在返回None
        """
        query = "SELECT * FROM comment_files WHERE post_id = ?"
        params = (post_id,)
        
        result = self.execute_query(query, params)
        return result[0] if result else None
    
    def update_comment_file(self, comment_file_id: int, post_id: str = None, is_hot: bool = None) -> bool:
        """
        更新评论文件
        
        Args:
            comment_file_id: 评论文件ID
            post_id: 帖子ID（可选）
            is_hot: 是否为热帖子评论文件（可选）
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        
        # 构建更新语句和参数
        update_fields = []
        update_params = []
        
        if post_id:
            update_fields.append("post_id = ?")
            update_params.append(post_id)
        if is_hot is not None:
            update_fields.append("is_hot = ?")
            update_params.append(1 if is_hot else 0)
        
        if not update_fields:
            return False
        
        update_fields.append("updated_at = ?")
        update_params.append(now)
        update_params.append(comment_file_id)
        
        query = f'''UPDATE comment_files SET {', '.join(update_fields)} WHERE id = ?''' 
        
        affected_rows = self.execute_update(query, tuple(update_params))
        return affected_rows > 0
    
    # 临时URL相关操作
    def add_temp_url(self, temp_url: str, actual_path: str, expires_at: str) -> bool:
        """
        添加临时URL
        
        Args:
            temp_url: 临时URL
            actual_path: 实际文件路径
            expires_at: 过期时间
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        query = '''
        INSERT INTO temp_urls (temp_url, actual_path, expires_at, accessed_at, created_at)
        VALUES (?, ?, ?, ?, ?)
        '''
        params = (temp_url, actual_path, expires_at, now, now)
        
        try:
            self.execute_update(query, params)
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_temp_url(self, temp_url: str) -> Optional[Dict[str, Any]]:
        """
        获取临时URL
        
        Args:
            temp_url: 临时URL
            
        Returns:
            Optional[Dict[str, Any]]: 临时URL信息，不存在返回None
        """
        query = "SELECT * FROM temp_urls WHERE temp_url = ?"
        params = (temp_url,)
        
        result = self.execute_query(query, params)
        return result[0] if result else None
    
    def update_temp_url_access(self, temp_url: str) -> bool:
        """
        更新临时URL的访问时间
        
        Args:
            temp_url: 临时URL
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        query = '''
        UPDATE temp_urls SET accessed_at = ? WHERE temp_url = ?
        '''
        params = (now, temp_url)
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def delete_expired_temp_urls(self) -> int:
        """
        删除过期的临时URL
        
        Returns:
            int: 删除的记录数
        """
        now = datetime.now().isoformat()
        query = "DELETE FROM temp_urls WHERE expires_at < ?"
        params = (now,)
        
        affected_rows = self.execute_update(query, params)
        return affected_rows