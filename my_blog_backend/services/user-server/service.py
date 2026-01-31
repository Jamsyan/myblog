from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import sys
import os

# 添加当前目录到sys.path，确保动态导入时能找到模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# 添加项目根目录到sys.path，以便导入LinkGateway模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import User, Asset
from passlib.context import CryptContext
from LinkGateway.logs import get_logger
from LinkGateway.service_comm import ServiceCommunicator

class UserServerService:
    """
    用户服务器业务逻辑类，负责处理用户相关的核心业务逻辑
    """
    
    def __init__(self, db: Session, service_comm: Optional[ServiceCommunicator] = None):
        """
        初始化用户服务器
        
        Args:
            db: 数据库会话
            service_comm: 服务层内部通信器（可选）
        """
        self.db = db
        self.service_comm = service_comm
        # 直接使用pbkdf2_sha256作为密码哈希算法，避免bcrypt的版本检查问题
        self.pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        self.logger = get_logger("user-server")
    
    def _call_engine(self, engine_id: str, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        通过内部通信调用引擎
        
        Args:
            engine_id: 引擎ID
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 请求结果
        """
        if self.service_comm is None:
            self.logger.warning(f"ServiceCommunicator not initialized, skipping engine call: {engine_id}/{action}")
            return {"error": "ServiceCommunicator not initialized"}
        return self.service_comm.call_engine(engine_id, action, data)
    
    def create_user(self, user_data: Dict[str, Any]) -> Optional[User]:
        """
        创建新用户
        
        Args:
            user_data: 用户数据，包含email, username, password, full_name等字段
            
        Returns:
            Optional[User]: 创建的用户对象，失败返回None
        """
        try:
            if self._username_exists(user_data.get("username")):
                return None
            
            if self._email_exists(user_data.get("email")):
                return None
            
            password_hash = self._hash_password(user_data.get("password"))
            permission_level, permissions = self._get_user_permissions(user_data)
            
            user = User(
                username=user_data.get("username"),
                email=user_data.get("email"),
                password_hash=password_hash,
                full_name=user_data.get("full_name"),
                permission_level=permission_level,
                permission_list=permissions
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            self.logger.info(f"User created successfully: {user.username}")
            return user
        except Exception as e:
            self.logger.error(f"Error creating user: {str(e)}")
            self.db.rollback()
            return None
    
    def _username_exists(self, username: str) -> bool:
        """
        检查用户名是否已存在
        
        Args:
            username: 用户名
            
        Returns:
            bool: 存在返回True，否则返回False
        """
        existing_user = self.get_user_by_username(username)
        if existing_user:
            self.logger.error(f"Username already exists: {username}")
            return True
        return False
    
    def _email_exists(self, email: str) -> bool:
        """
        检查邮箱是否已存在
        
        Args:
            email: 邮箱
            
        Returns:
            bool: 存在返回True，否则返回False
        """
        existing_email = self.db.query(User).filter(User.email == email).first()
        if existing_email:
            self.logger.error(f"Email already exists: {email}")
            return True
        return False
    
    def _hash_password(self, password: str) -> str:
        """
        生成密码哈希，确保密码长度不超过72字节
        
        Args:
            password: 密码
            
        Returns:
            str: 密码哈希
        """
        for i in range(3):
            try:
                password = password[:72 - i]
                return self.pwd_context.hash(password)
            except Exception:
                if i == 2:
                    return self.pwd_context.hash("")
                continue
        return self.pwd_context.hash("")
    
    def _get_user_permissions(self, user_data: Dict[str, Any]) -> tuple:
        """
        获取用户权限信息
        
        Args:
            user_data: 用户数据
            
        Returns:
            tuple: (permission_level, permissions)
        """
        permdog_result = self._call_engine("permdog", "get_default_permissions", {
            "user_info": {
                "username": user_data.get("username"),
                "email": user_data.get("email")
            }
        })
        
        if "error" in permdog_result:
            self.logger.error(f"Failed to get default permissions from PermDog: {permdog_result['error']}")
            return ("P3", ["view_post", "create_post", "edit_post"])
        
        permission_level = permdog_result.get("permission_level", "P3")
        permissions = permdog_result.get("permissions", ["view_post", "create_post", "edit_post"])
        return (permission_level, permissions)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        验证用户身份
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            Optional[User]: 验证成功返回用户对象，失败返回None
        """
        try:
            # 查找用户
            user = self.get_user_by_username(username)
            if not user or not user.is_active:
                return None
            
            # 验证密码
            if not self.pwd_context.verify(password, user.password_hash):
                return None
            
            self.logger.info(f"User authenticated successfully: {username}")
            return user
        except Exception as e:
            self.logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        根据ID获取用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[User]: 找到的用户对象，未找到返回None
        """
        return self.db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            Optional[User]: 找到的用户对象，未找到返回None
        """
        return self.db.query(User).filter(User.username == username, User.is_active == True).first()
    
    def update_user(self, user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            user_data: 更新的用户数据
            
        Returns:
            Optional[User]: 更新后的用户对象，未找到返回None
        """
        try:
            # 查找用户
            user = self.get_user(user_id)
            if not user:
                return None
            
            # 更新用户数据
            update_fields = ["email", "full_name", "permission_level"]
            for field in update_fields:
                if field in user_data:
                    setattr(user, field, user_data[field])
            
            # 单独处理密码更新
            if "password" in user_data and user_data["password"]:
                # 确保密码长度不超过72字节
                password = user_data["password"][:72]  # 截断密码，确保不超过72字节
                user.password_hash = self.pwd_context.hash(password)
            
            # 保存到数据库
            self.db.commit()
            self.db.refresh(user)
            
            self.logger.info(f"User updated successfully: {user.id}")
            return user
        except Exception as e:
            self.logger.error(f"Error updating user: {str(e)}")
            self.db.rollback()
            return None
    
    def get_user_permissions(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户权限
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 用户权限信息
        """
        user = self.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        return {
            "permission_level": user.permission_level,
            "permissions": user.permission_list
        }
    
    def get_user_pages(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户可访问页面
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 用户可访问页面信息
        """
        user = self.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        # 调用PermDog获取可访问页面
        result = self._call_engine("permdog", "get_allowed_pages", {
            "permission_level": user.permission_level,
            "permissions": user.permission_list
        })
        
        return result
    
    def get_user_tasks(self, user_id: int) -> Dict[str, Any]:
        """
        获取用户可访问任务
        
        Args:
            user_id: 用户ID
            
        Returns:
            Dict[str, Any]: 用户可访问任务信息
        """
        user = self.get_user(user_id)
        if not user:
            return {"error": "User not found"}
        
        # 调用PermDog获取可访问任务
        result = self._call_engine("permdog", "get_allowed_tasks", {
            "permission_level": user.permission_level,
            "permissions": user.permission_list
        })
        
        return result
    
    def create_asset(self, user_id: int, asset_id: str, asset_type: str = "post") -> Optional[Asset]:
        """
        创建用户资产
        
        Args:
            user_id: 用户ID
            asset_id: 资产ID
            asset_type: 资产类型
            
        Returns:
            Optional[Asset]: 创建的资产对象，失败返回None
        """
        try:
            # 检查用户是否存在
            user = self.get_user(user_id)
            if not user:
                return None
            
            # 检查资产是否已存在
            existing_asset = self.db.query(Asset).filter(Asset.asset_id == asset_id).first()
            if existing_asset:
                self.logger.error(f"Asset already exists: {asset_id}")
                return None
            
            # 创建资产对象
            asset = Asset(
                user_id=user_id,
                asset_type=asset_type,
                asset_id=asset_id
            )
            
            # 添加到数据库
            self.db.add(asset)
            self.db.commit()
            self.db.refresh(asset)
            
            self.logger.info(f"Asset created successfully: {asset.asset_id}")
            return asset
        except Exception as e:
            self.logger.error(f"Error creating asset: {str(e)}")
            self.db.rollback()
            return None
    
    def get_user_assets(self, user_id: int, asset_type: str = None) -> List[Asset]:
        """
        获取用户资产列表
        
        Args:
            user_id: 用户ID
            asset_type: 资产类型，可选
            
        Returns:
            List[Asset]: 用户资产列表
        """
        query = self.db.query(Asset).filter(Asset.user_id == user_id)
        
        if asset_type:
            query = query.filter(Asset.asset_type == asset_type)
        
        return query.all()
    
    def get_asset(self, asset_id: str) -> Optional[Asset]:
        """
        根据资产ID获取资产
        
        Args:
            asset_id: 资产ID
            
        Returns:
            Optional[Asset]: 找到的资产对象，未找到返回None
        """
        return self.db.query(Asset).filter(Asset.asset_id == asset_id).first()
    
    def update_asset_likes(self, asset_id: str, like_count: int) -> Optional[Asset]:
        """
        更新资产点赞数
        
        Args:
            asset_id: 资产ID
            like_count: 点赞数
            
        Returns:
            Optional[Asset]: 更新后的资产对象，未找到返回None
        """
        try:
            # 查找资产
            asset = self.get_asset(asset_id)
            if not asset:
                return None
            
            # 更新点赞数
            asset.like_count = like_count
            
            # 保存到数据库
            self.db.commit()
            self.db.refresh(asset)
            
            self.logger.info(f"Asset likes updated successfully: {asset.asset_id}, likes: {asset.like_count}")
            return asset
        except Exception as e:
            self.logger.error(f"Error updating asset likes: {str(e)}")
            self.db.rollback()
            return None
    
    def delete_asset(self, asset_id: str) -> bool:
        """
        删除资产
        
        Args:
            asset_id: 资产ID
            
        Returns:
            bool: 删除成功返回True，失败返回False
        """
        try:
            # 查找资产
            asset = self.get_asset(asset_id)
            if not asset:
                return False
            
            # 删除资产
            self.db.delete(asset)
            self.db.commit()
            
            self.logger.info(f"Asset deleted successfully: {asset_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting asset: {str(e)}")
            self.db.rollback()
            return False
