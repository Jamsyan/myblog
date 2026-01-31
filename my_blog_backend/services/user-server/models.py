from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json


Base = declarative_base()


class User(Base):
    """
    用户数据模型
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100))
    permission_level = Column(String(10), default="P3", nullable=False)
    permissions = Column(Text, default="[]", nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 定义与Asset的一对多关系
    assets = relationship("Asset", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', permission_level='{self.permission_level}')>"
    
    @property
    def permission_list(self):
        """
        获取权限列表
        """
        return json.loads(self.permissions)
    
    @permission_list.setter
    def permission_list(self, permissions):
        """
        设置权限列表
        """
        self.permissions = json.dumps(permissions)


class Asset(Base):
    """
    用户资产数据模型
    """
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    asset_type = Column(String(50), default="post", nullable=False)
    asset_id = Column(String(100), unique=True, nullable=False, index=True)
    like_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 定义与User的多对一关系
    user = relationship("User", back_populates="assets")
    
    def __repr__(self):
        return f"<Asset(id={self.id}, user_id={self.user_id}, asset_type='{self.asset_type}', asset_id='{self.asset_id}', like_count={self.like_count})>"