from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Dict, Any, Optional
import os
import sys
from datetime import datetime

# 添加当前目录到sys.path，确保动态导入时能找到模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 直接创建logger实例
import logging
logger = logging.getLogger(__name__)

# 创建基础模型类
Base = declarative_base()

# 点赞记录模型
class Like(Base):
    """
    点赞记录模型，用于记录用户对帖子的点赞
    """
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, index=True)  # 点赞用户ID
    post_id = Column(String(100), nullable=False, index=True)  # 帖子ID
    created_at = Column(DateTime, default=datetime.utcnow)  # 点赞时间

class InteractionDatabase:
    """
    互动服务数据库操作类，负责处理点赞和评论相关的数据库操作
    """
    
    def __init__(self, db_path: str):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{self.db_path}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # 创建所有表
        self._create_tables()
        
    def _create_tables(self):
        """
        创建所有表
        """
        try:
            # 创建likes表
            Like.__table__.create(self.engine, checkfirst=True)
            logger.debug("数据库表创建成功")
        except Exception as e:
            logger.error(f"数据库表创建失败: {str(e)}")
            raise
    
    def get_db(self) -> Session:
        """
        获取数据库会话
        
        Returns:
            Session: 数据库会话实例
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def get_like_count(self, db: Session, post_id: str) -> int:
        """
        获取帖子点赞数
        
        Args:
            db: 数据库会话
            post_id: 帖子ID
            
        Returns:
            int: 点赞数
        """
        try:
            # 从user-server的Asset表中获取点赞数
            # 这里需要注意，我们需要使用与user-server相同的数据库连接
            # 由于我们使用的是同一个数据库文件，所以可以直接查询
            from services.user_server.models import Asset
            asset = db.query(Asset).filter(Asset.asset_id == post_id).first()
            if asset:
                return asset.like_count
            return 0
        except Exception as e:
            logger.error(f"获取点赞数失败: {str(e)}")
            return 0
    
    def update_like_count(self, db: Session, post_id: str, increment: int = 1) -> Optional[int]:
        """
        更新帖子点赞数
        
        Args:
            db: 数据库会话
            post_id: 帖子ID
            increment: 增量，默认为1，表示增加点赞；-1表示减少点赞
            
        Returns:
            Optional[int]: 更新后的点赞数，失败返回None
        """
        try:
            # 从user-server的Asset表中更新点赞数
            from services.user_server.models import Asset
            asset = db.query(Asset).filter(Asset.asset_id == post_id).first()
            if asset:
                # 更新点赞数，确保点赞数不小于0
                asset.like_count = max(0, asset.like_count + increment)
                db.commit()
                db.refresh(asset)
                logger.debug(f"帖子 {post_id} 点赞数更新为 {asset.like_count}")
                return asset.like_count
            return None
        except Exception as e:
            logger.error(f"更新点赞数失败: {str(e)}")
            db.rollback()
            return None
    
    def add_like(self, db: Session, user_id: int, post_id: str) -> bool:
        """
        添加点赞记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            post_id: 帖子ID
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        try:
            # 检查是否已经点赞
            existing_like = db.query(Like).filter(
                Like.user_id == user_id, 
                Like.post_id == post_id
            ).first()
            
            if existing_like:
                logger.debug(f"用户 {user_id} 已点赞帖子 {post_id}")
                return False
            
            # 添加点赞记录
            like = Like(user_id=user_id, post_id=post_id)
            db.add(like)
            db.commit()
            logger.debug(f"用户 {user_id} 点赞帖子 {post_id} 成功")
            return True
        except Exception as e:
            logger.error(f"添加点赞记录失败: {str(e)}")
            db.rollback()
            return False
    
    def remove_like(self, db: Session, user_id: int, post_id: str) -> bool:
        """
        移除点赞记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            post_id: 帖子ID
            
        Returns:
            bool: 移除成功返回True，失败返回False
        """
        try:
            # 查找点赞记录
            like = db.query(Like).filter(
                Like.user_id == user_id, 
                Like.post_id == post_id
            ).first()
            
            if like:
                # 删除点赞记录
                db.delete(like)
                db.commit()
                logger.debug(f"用户 {user_id} 取消点赞帖子 {post_id} 成功")
                return True
            
            logger.debug(f"用户 {user_id} 未点赞帖子 {post_id}")
            return False
        except Exception as e:
            logger.error(f"移除点赞记录失败: {str(e)}")
            db.rollback()
            return False
    
    def is_liked(self, db: Session, user_id: int, post_id: str) -> bool:
        """
        检查用户是否已点赞帖子
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            post_id: 帖子ID
            
        Returns:
            bool: 已点赞返回True，否则返回False
        """
        try:
            like = db.query(Like).filter(
                Like.user_id == user_id, 
                Like.post_id == post_id
            ).first()
            return like is not None
        except Exception as e:
            logger.error(f"检查点赞状态失败: {str(e)}")
            return False
    
    def get_user_likes(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list:
        """
        获取用户点赞记录
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过的记录数
            limit: 返回的记录数
            
        Returns:
            list: 用户点赞记录列表
        """
        try:
            likes = db.query(Like).filter(
                Like.user_id == user_id
            ).order_by(Like.created_at.desc()).offset(skip).limit(limit).all()
            
            # 转换为字典列表
            return [{
                "post_id": like.post_id,
                "created_at": like.created_at.isoformat()
            } for like in likes]
        except Exception as e:
            logger.error(f"获取用户点赞记录失败: {str(e)}")
            return []