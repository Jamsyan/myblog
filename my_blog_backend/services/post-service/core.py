from typing import Dict, Any, Optional, List
import requests
import json
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import sys
import os

# 使用LinkGateway提供的日志模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from LinkGateway.logs import get_logger
logger = get_logger("post-service")


Base = declarative_base()


class Post(Base):
    """
    帖子数据模型
    """
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    post_id = Column(String(100), unique=True, nullable=False, index=True)  # 与FileEngine中的帖子ID对应
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    permission_level = Column(String(10), default="P3", nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(10), default="html", nullable=False)
    is_public = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Post(id={self.id}, post_id='{self.post_id}', title='{self.title}', user_id={self.user_id}, permission_level='{self.permission_level}')>"


class PostService:
    """
    帖子管理服务核心业务逻辑类
    """
    
    def __init__(self, db_path: str, linkgateway_url: str = "http://localhost:8000"):
        """
        初始化帖子管理服务
        
        Args:
            db_path: 数据库路径
            linkgateway_url: LinkGateway的访问地址
        """
        # 初始化数据库连接
        self.engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
        
        # 初始化LinkGateway通信
        self.linkgateway_url = linkgateway_url
        
        # 日志记录器
        self.logger = logger
        
        self.logger.info("帖子管理服务初始化成功")
    
    def _call_linkgateway(self, service_id: str, endpoint: str, method: str = "POST", data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        通过LinkGateway调用其他服务或引擎
        
        Args:
            service_id: 服务或引擎的ID
            endpoint: 端点路径
            method: 请求方法，默认为POST
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 请求结果
        """
        try:
            # 根据service_id和endpoint构建完整URL
            if service_id in ["permdog", "file_engine"]:
                # 引擎调用，使用/internal/proxy路径
                url = f"{self.linkgateway_url}/internal/proxy/{service_id}"
                payload = {
                    "action": endpoint,
                    "data": data or {}
                }
                response = requests.post(url, json=payload, timeout=10)
            else:
                # 服务调用，使用/api路径
                url = f"{self.linkgateway_url}/api/{service_id}{endpoint}"
                if method == "GET":
                    response = requests.get(url, params=data or {}, timeout=10)
                else:
                    response = requests.post(url, json=data or {}, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.logger.info(f"调用{service_id}服务成功: {result}")
                return result
            else:
                self.logger.error(f"调用{service_id}服务失败: {response.status_code}, {response.text}")
                return {"error": f"Failed to call {service_id}: {response.status_code}"}
        except Exception as e:
            self.logger.error(f"调用{service_id}服务时发生异常: {str(e)}")
            return {"error": str(e)}
    
    def _verify_permission(self, user_id: int, required_permission: str) -> bool:
        """
        验证用户是否具备所需权限
        
        Args:
            user_id: 用户ID
            required_permission: 所需权限
            
        Returns:
            bool: 具备权限返回True，否则返回False
        """
        try:
            # 调用user-server获取用户信息
            user_response = self._call_linkgateway("user-server", f"/users/{user_id}", method="GET")
            
            if "error" in user_response:
                self.logger.error(f"获取用户信息失败: {user_response['error']}")
                return False
            
            # 调用permdog验证权限
            permdog_response = self._call_linkgateway("permdog", "verify_permission", {
                "user_id": user_id,
                "permission": required_permission
            })
            
            if "error" in permdog_response:
                self.logger.error(f"验证权限失败: {permdog_response['error']}")
                return False
            
            return permdog_response.get("success", False)
        except Exception as e:
            self.logger.error(f"权限验证时发生异常: {str(e)}")
            return False
    
    def _get_user_permission_level(self, user_id: int) -> Optional[str]:
        """
        获取用户的权限等级
        
        Args:
            user_id: 用户ID
            
        Returns:
            Optional[str]: 用户的权限等级，如"P0"、"P1"等，失败返回None
        """
        try:
            # 调用user-server获取用户信息
            user_response = self._call_linkgateway("user-server", f"/users/{user_id}", method="GET")
            
            if "error" in user_response:
                self.logger.error(f"获取用户信息失败: {user_response['error']}")
                return None
            
            return user_response.get("permission_level")
        except Exception as e:
            self.logger.error(f"获取用户权限等级时发生异常: {str(e)}")
            return None
    
    def _is_permission_valid(self, current_level: str, new_level: str) -> bool:
        """
        验证权限调整是否有效：只能向下调整权限等级
        
        Args:
            current_level: 当前权限等级
            new_level: 新的权限等级
            
        Returns:
            bool: 权限调整有效返回True，否则返回False
        """
        try:
            # 权限等级转换为数字，数字越小权限越高
            current_num = int(current_level.replace("P", ""))
            new_num = int(new_level.replace("P", ""))
            
            # 只能向下调整权限（新权限数字大于或等于当前权限数字）
            return new_num >= current_num
        except Exception as e:
            self.logger.error(f"权限等级转换失败: {str(e)}")
            return False
    
    def create_post(self, user_id: int, title: str, content: str, permission_level: str = "P3") -> Dict[str, Any]:
        """
        创建帖子
        
        Args:
            user_id: 用户ID
            title: 帖子标题
            content: 帖子内容
            permission_level: 帖子权限等级
            
        Returns:
            Dict[str, Any]: 创建结果
        """
        try:
            # 验证用户是否具备创建帖子的权限
            if not self._verify_permission(user_id, "create_post"):
                return {
                    "error": "无权限发送帖子，请联系管理员",
                    "status": "error"
                }
            
            # 获取用户的权限等级
            user_perm_level = self._get_user_permission_level(user_id)
            if not user_perm_level:
                return {
                    "error": "获取用户权限失败",
                    "status": "error"
                }
            
            # 调用FileEngine创建帖子
            file_engine_response = self._call_linkgateway("file_engine", "create_post", {
                "title": title,
                "content": content,
                "permission_level": permission_level,
                "created_by": str(user_id)
            })
            
            if "error" in file_engine_response:
                return {
                    "error": f"创建帖子失败: {file_engine_response['error']}",
                    "status": "error"
                }
            
            post_id = file_engine_response.get("post_id")
            if not post_id:
                return {
                    "error": "创建帖子失败: 未返回帖子ID",
                    "status": "error"
                }
            
            # 保存帖子信息到数据库
            new_post = Post(
                post_id=post_id,
                title=title,
                content=content,
                user_id=user_id,
                permission_level=permission_level,
                file_path=file_engine_response.get("file_path", ""),
                file_type=file_engine_response.get("file_type", "html"),
                is_public=True
            )
            
            self.db.add(new_post)
            self.db.commit()
            self.db.refresh(new_post)
            
            return {
                "success": True,
                "post_id": post_id,
                "message": "帖子创建成功",
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"创建帖子时发生异常: {str(e)}")
            self.db.rollback()
            return {
                "error": f"创建帖子时发生异常: {str(e)}",
                "status": "error"
            }
    
    def get_post(self, post_id: str, user_id: int) -> Dict[str, Any]:
        """
        获取单个帖子
        
        Args:
            post_id: 帖子ID
            user_id: 用户ID（用于权限验证）
            
        Returns:
            Dict[str, Any]: 帖子信息
        """
        try:
            # 从数据库获取帖子信息
            post = self.db.query(Post).filter(Post.post_id == post_id).first()
            if not post:
                return {
                    "error": "帖子不存在",
                    "status": "error"
                }
            
            # 获取当前用户的权限等级
            current_user_perm = self._get_user_permission_level(user_id)
            if not current_user_perm:
                return {
                    "error": "获取用户权限失败",
                    "status": "error"
                }
            
            # 验证用户是否有权限查看该帖子
            # 低权限用户只能查看比自己权限低或相等的用户发布的帖子
            if current_user_perm > post.permission_level:
                return {
                    "error": "无权限查看该帖子",
                    "status": "error"
                }
            
            # 调用FileEngine获取帖子内容
            file_engine_response = self._call_linkgateway("file_engine", "get_post", {
                "post_id": post_id
            })
            
            if "error" in file_engine_response:
                return {
                    "error": f"获取帖子内容失败: {file_engine_response['error']}",
                    "status": "error"
                }
            
            return {
                "success": True,
                "data": {
                    "post_id": post.post_id,
                    "title": post.title,
                    "content": file_engine_response.get("content", ""),
                    "user_id": post.user_id,
                    "permission_level": post.permission_level,
                    "file_type": post.file_type,
                    "created_at": post.created_at.isoformat(),
                    "updated_at": post.updated_at.isoformat()
                },
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"获取帖子时发生异常: {str(e)}")
            return {
                "error": f"获取帖子时发生异常: {str(e)}",
                "status": "error"
            }
    
    def get_posts(self, user_id: int, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        获取帖子列表（带权限过滤）
        
        Args:
            user_id: 用户ID（用于权限验证）
            page: 页码
            limit: 每页数量
            
        Returns:
            Dict[str, Any]: 帖子列表
        """
        try:
            # 获取当前用户的权限等级
            current_user_perm = self._get_user_permission_level(user_id)
            if not current_user_perm:
                return {
                    "error": "获取用户权限失败",
                    "status": "error"
                }
            
            # 计算偏移量
            offset = (page - 1) * limit
            
            # 查询数据库获取帖子列表，按权限等级过滤
            posts = self.db.query(Post).filter(Post.permission_level <= current_user_perm).offset(offset).limit(limit).all()
            total = self.db.query(Post).filter(Post.permission_level <= current_user_perm).count()
            
            # 构建返回结果
            post_list = []
            for post in posts:
                post_list.append({
                    "post_id": post.post_id,
                    "title": post.title,
                    "user_id": post.user_id,
                    "permission_level": post.permission_level,
                    "file_type": post.file_type,
                    "created_at": post.created_at.isoformat(),
                    "updated_at": post.updated_at.isoformat()
                })
            
            return {
                "success": True,
                "data": {
                    "posts": post_list,
                    "total": total,
                    "page": page,
                    "limit": limit
                },
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"获取帖子列表时发生异常: {str(e)}")
            return {
                "error": f"获取帖子列表时发生异常: {str(e)}",
                "status": "error"
            }
    
    def update_post(self, post_id: str, user_id: int, title: Optional[str] = None, content: Optional[str] = None, permission_level: Optional[str] = None) -> Dict[str, Any]:
        """
        更新帖子
        
        Args:
            post_id: 帖子ID
            user_id: 用户ID（用于权限验证）
            title: 新标题（可选）
            content: 新内容（可选）
            permission_level: 新权限等级（可选）
            
        Returns:
            Dict[str, Any]: 更新结果
        """
        try:
            # 从数据库获取帖子信息
            post = self.db.query(Post).filter(Post.post_id == post_id).first()
            if not post:
                return {
                    "error": "帖子不存在",
                    "status": "error"
                }
            
            # 验证用户是否为帖子所有者或具备更高权限
            if post.user_id != user_id and not self._verify_permission(user_id, "admin_post"):
                return {
                    "error": "无权限更新该帖子",
                    "status": "error"
                }
            
            # 验证权限等级调整是否有效（只能向下调整）
            if permission_level and post.permission_level != permission_level and not self._is_permission_valid(post.permission_level, permission_level):
                return {
                    "error": "权限等级只能向下调整",
                    "status": "error"
                }
            
            # 调用FileEngine更新帖子
            file_engine_data = {}
            if title:
                file_engine_data["title"] = title
            if content:
                file_engine_data["content"] = content
            if permission_level:
                file_engine_data["permission_level"] = permission_level
            
            file_engine_response = self._call_linkgateway("file_engine", "update_post", {
                "post_id": post_id,
                **file_engine_data
            })
            
            if "error" in file_engine_response:
                return {
                    "error": f"更新帖子失败: {file_engine_response['error']}",
                    "status": "error"
                }
            
            # 更新数据库中的帖子信息
            if title:
                post.title = title
            if content:
                post.content = content
            if permission_level:
                post.permission_level = permission_level
            
            post.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(post)
            
            return {
                "success": True,
                "message": "帖子更新成功",
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"更新帖子时发生异常: {str(e)}")
            self.db.rollback()
            return {
                "error": f"更新帖子时发生异常: {str(e)}",
                "status": "error"
            }
    
    def delete_post(self, post_id: str, user_id: int) -> Dict[str, Any]:
        """
        删除帖子
        
        Args:
            post_id: 帖子ID
            user_id: 用户ID（用于权限验证）
            
        Returns:
            Dict[str, Any]: 删除结果
        """
        try:
            # 从数据库获取帖子信息
            post = self.db.query(Post).filter(Post.post_id == post_id).first()
            if not post:
                return {
                    "error": "帖子不存在",
                    "status": "error"
                }
            
            # 验证用户是否为帖子所有者或具备更高权限
            if post.user_id != user_id and not self._verify_permission(user_id, "admin_post"):
                return {
                    "error": "无权限删除该帖子",
                    "status": "error"
                }
            
            # 调用FileEngine删除帖子
            file_engine_response = self._call_linkgateway("file_engine", "delete_post", {
                "post_id": post_id
            })
            
            if "error" in file_engine_response:
                return {
                    "error": f"删除帖子失败: {file_engine_response['error']}",
                    "status": "error"
                }
            
            # 从数据库删除帖子
            self.db.delete(post)
            self.db.commit()
            
            return {
                "success": True,
                "message": "帖子删除成功",
                "status": "success"
            }
        except Exception as e:
            self.logger.error(f"删除帖子时发生异常: {str(e)}")
            self.db.rollback()
            return {
                "error": f"删除帖子时发生异常: {str(e)}",
                "status": "error"
            }
    
    def close(self):
        """
        关闭服务，释放资源
        """
        self.db.close()
