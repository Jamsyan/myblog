import os
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

from database import DatabaseManager
from logger import Logger


DEFAULT_PERMISSION_LEVELS = [
    {"level": "p0", "name": "最高权限", "is_default": 0},
    {"level": "p1", "name": "管理员权限", "is_default": 0},
    {"level": "p2", "name": "普通用户权限", "is_default": 0},
    {"level": "p3", "name": "默认权限", "is_default": 1}
]


class PermissionManager:
    """
    权限管理类，负责处理权限配置文件的读写和权限检查逻辑
    """
    
    def __init__(self, data_dir: str, db_manager: DatabaseManager, logger: Logger):
        """
        初始化权限管理器
        
        Args:
            data_dir: 数据目录路径
            db_manager: 数据库管理器实例
            logger: 日志记录器实例
        """
        self.data_dir = data_dir
        self.permission_dir = os.path.join(self.data_dir, "permissions")
        self.db_manager = db_manager
        self.logger = logger
        
        # 权限配置内存缓存
        self.permission_cache = {}
        
        # 确保权限配置目录存在
        os.makedirs(self.permission_dir, exist_ok=True)
    
    def _get_config_path(self, permission_level: str) -> str:
        """
        获取权限配置文件路径
        
        Args:
            permission_level: 权限等级
            
        Returns:
            str: 配置文件路径
        """
        return os.path.join(self.permission_dir, f"{permission_level}.json")
    
    def _preload_permissions(self):
        """
        预加载所有权限配置到内存
        """
        self.logger.info("开始预加载所有权限配置到内存")
        
        # 清空缓存
        self.permission_cache.clear()
        
        # 获取所有权限等级
        try:
            if hasattr(self.db_manager, 'list_permission_levels'):
                permission_levels = self.db_manager.list_permission_levels()
                
                for perm_level in permission_levels:
                    level = perm_level["level"]
                    # 加载权限配置
                    config = self.load_permission_config(level)
                    if config:
                        # 将配置存储到内存缓存
                        self.permission_cache[level] = {
                            "allowed_operations": config.get("allowed_operations", []),
                            "allowed_components": config.get("allowed_components", [])
                        }
                
                self.logger.info(f"权限配置预加载完成，共加载 {len(self.permission_cache)} 个权限等级")
            else:
                self.logger.warning("DatabaseManager对象没有list_permission_levels方法")
        except Exception as e:
            self.logger.error(f"预加载权限配置时发生错误: {str(e)}")
    
    def reload_permissions(self) -> bool:
        """
        重新加载所有权限配置到内存（热更新）
        
        Returns:
            bool: 加载成功返回True，失败返回False
        """
        try:
            self._preload_permissions()
            self.logger.info("权限配置热更新成功")
            return True
        except Exception as e:
            self.logger.error(f"权限配置热更新失败: {str(e)}")
            return False
    
    def load_permission_config(self, permission_level: str) -> Optional[Dict[str, Any]]:
        """
        加载指定权限等级的配置
        
        Args:
            permission_level: 权限等级
            
        Returns:
            Optional[Dict[str, Any]]: 权限配置，不存在返回None
        """
        config_path = self._get_config_path(permission_level)
        
        if not os.path.exists(config_path):
            self.logger.warning(f"权限配置文件不存在: {config_path}")
            return None
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            self.logger.info(f"加载权限配置成功: {permission_level}")
            return config
        except json.JSONDecodeError as e:
            self.logger.error(f"解析权限配置文件失败: {permission_level}, 错误: {str(e)}")
            return None
        except Exception as e:
            self.logger.error(f"加载权限配置失败: {permission_level}, 错误: {str(e)}")
            return None
    
    def save_permission_config(self, permission_level: str, config: Dict[str, Any]) -> bool:
        """
        保存权限配置
        
        Args:
            permission_level: 权限等级
            config: 权限配置
            
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        config_path = self._get_config_path(permission_level)
        
        try:
            # 更新配置时间
            config["updated_at"] = datetime.now().isoformat()
            
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            
            # 更新数据库中的配置信息
            self.db_manager.update_permission_config(permission_level, config_path)
            
            self.logger.info(f"保存权限配置成功: {permission_level}")
            return True
        except Exception as e:
            self.logger.error(f"保存权限配置失败: {permission_level}, 错误: {str(e)}")
            return False
    
    def get_default_permission(self) -> Dict[str, Any]:
        """
        获取默认权限等级
        
        Returns:
            Dict[str, Any]: 默认权限等级信息
        """
        # 从数据库获取默认权限等级
        default_perm = self.db_manager.get_default_permission_level()
        
        if default_perm:
            self.logger.info(f"获取默认权限成功: {default_perm['level']}")
            return {
                "permission_level": default_perm["level"],
                "name": default_perm["name"],
                "status": "success"
            }
        else:
            # 默认返回p3权限
            self.logger.warning("未找到默认权限，返回默认p3权限")
            return {
                "permission_level": "p3",
                "name": "默认权限",
                "status": "success"
            }
    
    def set_default_permission(self, permission_level: str) -> bool:
        """
        设置默认权限等级
        
        Args:
            permission_level: 权限等级
            
        Returns:
            bool: 设置成功返回True，失败返回False
        """
        try:
            # 先将所有权限等级的is_default设为0
            self.db_manager.execute_update("UPDATE permission_levels SET is_default = 0")
            
            # 将指定权限等级的is_default设为1
            success = self.db_manager.update_permission_level(permission_level, is_default=True)
            
            if success:
                self.logger.info(f"设置默认权限成功: {permission_level}")
            else:
                self.logger.error(f"设置默认权限失败: {permission_level}")
            
            return success
        except Exception as e:
            self.logger.error(f"设置默认权限失败: {permission_level}, 错误: {str(e)}")
            return False
    
    def check_operation_permission(self, permission_level: str, operation_name: str) -> Dict[str, Any]:
        """
        检查用户是否有权执行操作
        
        Args:
            permission_level: 权限等级
            operation_name: 操作名称
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        # 从内存缓存中获取权限配置
        if permission_level not in self.permission_cache:
            self.logger.error(f"权限等级不存在于缓存中: {permission_level}")
            return {
                "allowed": False,
                "permission_level": permission_level,
                "operation_name": operation_name,
                "status": "error",
                "message": f"Permission level '{permission_level}' not found in cache"
            }
        
        # 从缓存中获取允许的操作列表
        allowed_operations = self.permission_cache[permission_level]["allowed_operations"]
        allowed = operation_name in allowed_operations
        
        self.logger.debug(f"权限检查: {permission_level} - {operation_name} - {'允许' if allowed else '拒绝'}")
        
        return {
            "allowed": allowed,
            "permission_level": permission_level,
            "operation_name": operation_name,
            "status": "success"
        }
    
    def check_component_permission(self, permission_level: str, component_id: str) -> Dict[str, Any]:
        """
        检查用户是否有权访问组件
        
        Args:
            permission_level: 权限等级
            component_id: 组件ID
            
        Returns:
            Dict[str, Any]: 检查结果
        """
        # 从内存缓存中获取权限配置
        if permission_level not in self.permission_cache:
            self.logger.error(f"权限等级不存在于缓存中: {permission_level}")
            return {
                "allowed": False,
                "permission_level": permission_level,
                "component_id": component_id,
                "status": "error",
                "message": f"Permission level '{permission_level}' not found in cache"
            }
        
        # 从缓存中获取允许的组件列表
        allowed_components = self.permission_cache[permission_level]["allowed_components"]
        allowed = component_id in allowed_components
        
        self.logger.debug(f"组件权限检查: {permission_level} - {component_id} - {'允许' if allowed else '拒绝'}")
        
        return {
            "allowed": allowed,
            "permission_level": permission_level,
            "component_id": component_id,
            "status": "success"
        }
    
    def update_permission_config(self, permission_level: str, allowed_operations: List[str], allowed_components: List[str]) -> bool:
        """
        更新权限配置
        
        Args:
            permission_level: 权限等级
            allowed_operations: 允许的操作列表
            allowed_components: 允许的组件列表
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        # 加载现有配置
        config = self.load_permission_config(permission_level)
        
        if not config:
            # 获取权限等级名称
            perm_level = self.db_manager.get_permission_level(permission_level)
            name = perm_level["name"] if perm_level else permission_level
            
            # 创建新配置
            config = {
                "permission_level": permission_level,
                "name": name,
                "allowed_operations": [],
                "allowed_components": [],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        
        # 更新配置
        config["allowed_operations"] = allowed_operations
        config["allowed_components"] = allowed_components
        
        # 保存配置到文件
        if self.save_permission_config(permission_level, config):
            # 更新内存缓存
            self.permission_cache[permission_level] = {
                "allowed_operations": allowed_operations,
                "allowed_components": allowed_components
            }
            self.logger.info(f"权限配置更新成功，内存缓存已更新: {permission_level}")
            return True
        
        return False
    
    def init_default_permissions(self):
        """
        初始化默认权限配置
        """
        self.logger.info("开始初始化默认权限配置")
        
        for level_config in DEFAULT_PERMISSION_LEVELS:
            self._init_permission_level(level_config)
        
        self.logger.info("默认权限配置初始化完成")
    
    def _init_permission_level(self, level_config: Dict[str, Any]):
        """
        初始化单个权限等级
        
        Args:
            level_config: 权限等级配置
        """
        level = level_config["level"]
        name = level_config["name"]
        is_default = level_config["is_default"]
        
        self._add_permission_level_to_db(level, name, is_default)
        self._init_permission_config_file(level, name)
    
    def _add_permission_level_to_db(self, level: str, name: str, is_default: int):
        """
        添加权限等级到数据库
        
        Args:
            level: 权限等级
            name: 权限名称
            is_default: 是否为默认权限
        """
        if self._permission_level_exists(level):
            return
        
        if not hasattr(self.db_manager, 'add_permission_level'):
            return
        
        try:
            self.db_manager.add_permission_level(level, name, is_default)
            self.logger.info(f"添加权限等级: {level}")
        except Exception as e:
            self.logger.error(f"添加权限等级 {level} 时发生错误: {str(e)}")
    
    def _permission_level_exists(self, level: str) -> bool:
        """
        检查权限等级是否已存在
        
        Args:
            level: 权限等级
            
        Returns:
            bool: 存在返回True，否则返回False
        """
        if not hasattr(self.db_manager, 'get_permission_level'):
            return False
        
        try:
            return bool(self.db_manager.get_permission_level(level))
        except Exception as e:
            self.logger.warning(f"检查权限等级是否存在时发生错误: {str(e)}")
            return False
    
    def _init_permission_config_file(self, level: str, name: str):
        """
        初始化权限配置文件
        
        Args:
            level: 权限等级
            name: 权限名称
        """
        config_path = self._get_config_path(level)
        if os.path.exists(config_path):
            return
        
        self._create_permission_config_file(config_path, level, name)
        self._add_permission_config_to_db(level, config_path)
    
    def _create_permission_config_file(self, config_path: str, level: str, name: str):
        """
        创建权限配置文件
        
        Args:
            config_path: 配置文件路径
            level: 权限等级
            name: 权限名称
        """
        default_config = {
            "permission_level": level,
            "name": name,
            "allowed_operations": [],
            "allowed_components": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
    
    def _add_permission_config_to_db(self, level: str, config_path: str):
        """
        添加权限配置到数据库
        
        Args:
            level: 权限等级
            config_path: 配置文件路径
        """
        if not hasattr(self.db_manager, 'add_permission_config'):
            return
        
        try:
            self.db_manager.add_permission_config(level, config_path)
            self.logger.info(f"创建默认权限配置文件: {level}")
        except Exception as e:
            self.logger.error(f"添加权限配置 {level} 时发生错误: {str(e)}")
    
    def register_operation(self, operation_name: str, description: str = "") -> Dict[str, Any]:
        """
        注册可执行操作
        
        Args:
            operation_name: 操作名称
            description: 操作描述
            
        Returns:
            Dict[str, Any]: 注册结果
        """
        if self._operation_exists(operation_name):
            return {
                "error": f"Operation '{operation_name}' already exists",
                "status": "error"
            }
        
        return self._add_operation_to_db(operation_name, description)
    
    def _operation_exists(self, operation_name: str) -> bool:
        """
        检查操作是否已存在
        
        Args:
            operation_name: 操作名称
            
        Returns:
            bool: 存在返回True，否则返回False
        """
        if self.db_manager.get_operation(operation_name):
            self.logger.warning(f"操作已存在: {operation_name}")
            return True
        return False
    
    def _add_operation_to_db(self, operation_name: str, description: str) -> Dict[str, Any]:
        """
        添加操作到数据库
        
        Args:
            operation_name: 操作名称
            description: 操作描述
            
        Returns:
            Dict[str, Any]: 添加结果
        """
        try:
            success = self.db_manager.add_operation(operation_name, description)
            
            if success:
                self.logger.info(f"注册操作成功: {operation_name}")
                return {
                    "message": f"Operation '{operation_name}' registered successfully",
                    "operation_name": operation_name,
                    "status": "success"
                }
            
            self.logger.error(f"注册操作失败: {operation_name}")
            return {
                "error": f"Failed to register operation '{operation_name}'",
                "status": "error"
            }
        except Exception as e:
            self.logger.error(f"注册操作失败: {operation_name}, 错误: {str(e)}")
            return {
                "error": f"Error registering operation: {str(e)}",
                "status": "error"
            }
    
    def register_component(self, component_id: str, component_name: str, description: str = "") -> Dict[str, Any]:
        """
        注册前端组件
        
        Args:
            component_id: 组件ID
            component_name: 组件名称
            description: 组件描述
            
        Returns:
            Dict[str, Any]: 注册结果
        """
        if self._component_exists(component_id):
            return {
                "error": f"Component with id '{component_id}' already exists",
                "status": "error"
            }
        
        return self._add_component_to_db(component_id, component_name, description)
    
    def _component_exists(self, component_id: str) -> bool:
        """
        检查组件是否已存在
        
        Args:
            component_id: 组件ID
            
        Returns:
            bool: 存在返回True，否则返回False
        """
        if self.db_manager.get_component(component_id):
            self.logger.warning(f"组件已存在: {component_id}")
            return True
        return False
    
    def _add_component_to_db(self, component_id: str, component_name: str, description: str) -> Dict[str, Any]:
        """
        添加组件到数据库
        
        Args:
            component_id: 组件ID
            component_name: 组件名称
            description: 组件描述
            
        Returns:
            Dict[str, Any]: 添加结果
        """
        try:
            success = self.db_manager.add_component(component_id, component_name, description)
            
            if success:
                self.logger.info(f"注册组件成功: {component_id}")
                return {
                    "message": f"Component '{component_name}' registered successfully",
                    "component_id": component_id,
                    "component_name": component_name,
                    "status": "success"
                }
            
            self.logger.error(f"注册组件失败: {component_id}")
            return {
                "error": f"Failed to register component '{component_id}'",
                "status": "error"
            }
        except Exception as e:
            self.logger.error(f"注册组件失败: {component_id}, 错误: {str(e)}")
            return {
                "error": f"Error registering component: {str(e)}",
                "status": "error"
            }