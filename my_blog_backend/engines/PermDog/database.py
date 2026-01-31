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
        
        # 创建权限等级定义表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS permission_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            level TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            is_default INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # 创建可执行操作注册表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS permission_operations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            operation_name TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # 创建前端组件注册表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS permission_components (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            component_id TEXT NOT NULL UNIQUE,
            component_name TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        ''')
        
        # 创建权限配置索引表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS permission_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            permission_level TEXT NOT NULL,
            config_path TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (permission_level) REFERENCES permission_levels(level)
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
    
    # 权限等级相关操作
    def add_permission_level(self, level: str, name: str, is_default: bool = False) -> bool:
        """
        添加权限等级
        
        Args:
            level: 权限等级代码
            name: 权限等级名称
            is_default: 是否为默认权限
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        query = '''
        INSERT INTO permission_levels (level, name, is_default, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        '''
        params = (level, name, 1 if is_default else 0, now, now)
        
        try:
            self.execute_update(query, params)
            return True
        except sqlite3.IntegrityError:
            return False
    
    def update_permission_level(self, level: str, name: str = None, is_default: bool = None) -> bool:
        """
        更新权限等级
        
        Args:
            level: 权限等级代码
            name: 权限等级名称（可选）
            is_default: 是否为默认权限（可选）
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        
        if name and is_default is not None:
            query = '''
            UPDATE permission_levels
            SET name = ?, is_default = ?, updated_at = ?
            WHERE level = ?
            '''
            params = (name, 1 if is_default else 0, now, level)
        elif name:
            query = '''
            UPDATE permission_levels
            SET name = ?, updated_at = ?
            WHERE level = ?
            '''
            params = (name, now, level)
        elif is_default is not None:
            query = '''
            UPDATE permission_levels
            SET is_default = ?, updated_at = ?
            WHERE level = ?
            '''
            params = (1 if is_default else 0, now, level)
        else:
            return False
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def get_permission_level(self, level: str) -> Optional[Dict[str, Any]]:
        """
        获取指定权限等级
        
        Args:
            level: 权限等级代码
            
        Returns:
            Optional[Dict[str, Any]]: 权限等级信息，不存在返回None
        """
        query = "SELECT * FROM permission_levels WHERE level = ?"
        params = (level,)
        
        result = self.execute_query(query, params)
        return result[0] if result else None
    
    def get_default_permission_level(self) -> Optional[Dict[str, Any]]:
        """
        获取默认权限等级
        
        Returns:
            Optional[Dict[str, Any]]: 默认权限等级信息，不存在返回None
        """
        query = "SELECT * FROM permission_levels WHERE is_default = 1"
        
        result = self.execute_query(query)
        return result[0] if result else None
    
    def list_permission_levels(self) -> List[Dict[str, Any]]:
        """
        获取所有权限等级
        
        Returns:
            List[Dict[str, Any]]: 权限等级列表
        """
        query = "SELECT * FROM permission_levels ORDER BY level"
        return self.execute_query(query)
    
    # 操作注册相关操作
    def add_operation(self, operation_name: str, description: str = "") -> bool:
        """
        添加可执行操作
        
        Args:
            operation_name: 操作名称
            description: 操作描述
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        query = '''
        INSERT INTO permission_operations (operation_name, description, created_at, updated_at)
        VALUES (?, ?, ?, ?)
        '''
        params = (operation_name, description, now, now)
        
        try:
            self.execute_update(query, params)
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_operation(self, operation_name: str) -> Optional[Dict[str, Any]]:
        """
        获取指定操作
        
        Args:
            operation_name: 操作名称
            
        Returns:
            Optional[Dict[str, Any]]: 操作信息，不存在返回None
        """
        query = "SELECT * FROM permission_operations WHERE operation_name = ?"
        params = (operation_name,)
        
        result = self.execute_query(query, params)
        return result[0] if result else None
    
    def list_operations(self) -> List[Dict[str, Any]]:
        """
        获取所有操作
        
        Returns:
            List[Dict[str, Any]]: 操作列表
        """
        query = "SELECT * FROM permission_operations ORDER BY operation_name"
        return self.execute_query(query)
    
    # 组件注册相关操作
    def add_component(self, component_id: str, component_name: str, description: str = "") -> bool:
        """
        添加前端组件
        
        Args:
            component_id: 组件ID
            component_name: 组件名称
            description: 组件描述
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        query = '''
        INSERT INTO permission_components (component_id, component_name, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        '''
        params = (component_id, component_name, description, now, now)
        
        try:
            self.execute_update(query, params)
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_component(self, component_id: str) -> Optional[Dict[str, Any]]:
        """
        获取指定组件
        
        Args:
            component_id: 组件ID
            
        Returns:
            Optional[Dict[str, Any]]: 组件信息，不存在返回None
        """
        query = "SELECT * FROM permission_components WHERE component_id = ?"
        params = (component_id,)
        
        result = self.execute_query(query, params)
        return result[0] if result else None
    
    def list_components(self) -> List[Dict[str, Any]]:
        """
        获取所有组件
        
        Returns:
            List[Dict[str, Any]]: 组件列表
        """
        query = "SELECT * FROM permission_components ORDER BY component_id"
        return self.execute_query(query)
    
    # 权限配置相关操作
    def add_permission_config(self, permission_level: str, config_path: str, status: str = "active") -> bool:
        """
        添加权限配置
        
        Args:
            permission_level: 权限等级
            config_path: 配置文件路径
            status: 配置状态
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        query = '''
        INSERT INTO permission_configs (permission_level, config_path, last_updated, status)
        VALUES (?, ?, ?, ?)
        '''
        params = (permission_level, config_path, now, status)
        
        try:
            self.execute_update(query, params)
            return True
        except sqlite3.IntegrityError:
            return False
    
    def update_permission_config(self, permission_level: str, config_path: str = None, status: str = None) -> bool:
        """
        更新权限配置
        
        Args:
            permission_level: 权限等级
            config_path: 配置文件路径（可选）
            status: 配置状态（可选）
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        now = datetime.now().isoformat()
        
        if config_path and status:
            query = '''
            UPDATE permission_configs
            SET config_path = ?, last_updated = ?, status = ?
            WHERE permission_level = ?
            '''
            params = (config_path, now, status, permission_level)
        elif config_path:
            query = '''
            UPDATE permission_configs
            SET config_path = ?, last_updated = ?
            WHERE permission_level = ?
            '''
            params = (config_path, now, permission_level)
        elif status:
            query = '''
            UPDATE permission_configs
            SET last_updated = ?, status = ?
            WHERE permission_level = ?
            '''
            params = (now, status, permission_level)
        else:
            return False
        
        affected_rows = self.execute_update(query, params)
        return affected_rows > 0
    
    def get_permission_config(self, permission_level: str) -> Optional[Dict[str, Any]]:
        """
        获取指定权限等级的配置
        
        Args:
            permission_level: 权限等级
            
        Returns:
            Optional[Dict[str, Any]]: 权限配置信息，不存在返回None
        """
        query = "SELECT * FROM permission_configs WHERE permission_level = ?"
        params = (permission_level,)
        
        result = self.execute_query(query, params)
        return result[0] if result else None
    
    def list_permission_configs(self) -> List[Dict[str, Any]]:
        """
        获取所有权限配置
        
        Returns:
            List[Dict[str, Any]]: 权限配置列表
        """
        query = "SELECT * FROM permission_configs ORDER BY permission_level"
        return self.execute_query(query)