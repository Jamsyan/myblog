import os
from sqlalchemy import Column, String, Integer, Boolean, Text, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from datetime import datetime
from enum import Enum as PyEnum

# 创建基本模型类
Base = declarative_base()

# 服务类型枚举
class ServiceType(PyEnum):
    BUSINESS = "business"
    ENGINE = "engine"

# 引擎类型枚举
class EngineType(PyEnum):
    NETWORK = "network"
    KERNEL = "kernel"

# 服务状态枚举
class ServiceStatus(PyEnum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"

# 服务注册信息模型
class ServiceRegistry(Base):
    __tablename__ = "service_registry"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    service_id = Column(String(255), unique=True, index=True, nullable=False)
    service_name = Column(String(255), nullable=False)
    service_type = Column(Enum(ServiceType), nullable=False)
    version = Column(String(50), nullable=False)
    status = Column(Enum(ServiceStatus), default=ServiceStatus.UNKNOWN, nullable=False)
    reason = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    last_check_at = Column(DateTime, nullable=True)
    
    # 业务服务特有字段
    database_config = Column(Text, nullable=True)  # JSON格式存储数据库配置
    api_config = Column(Text, nullable=True)  # JSON格式存储API配置
    business_path = Column(String(500), nullable=True)
    
    # 引擎特有字段
    engine_type = Column(Enum(EngineType), nullable=True)
    engine_path = Column(String(500), nullable=True)

# 数据库连接管理器
class DatabaseManager:
    def __init__(self, db_path: str):
        """
        初始化数据库连接管理器
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.engine = None
        self.SessionLocal = None
        
        # 初始化数据库
        self._init_db()
    
    def _init_db(self):
        """
        初始化数据库连接和表结构
        """
        # 确保数据库目录存在
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        # 创建SQLAlchemy引擎，添加线程安全配置和超时设置
        self.engine = create_engine(
            f"sqlite:///{self.db_path}",
            connect_args={"check_same_thread": False, "timeout": 10},
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False
        )
        
        # 创建SessionLocal类
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # 创建所有表（带重试机制）
        self._create_tables_with_retry()
    
    def _create_tables_with_retry(self, max_retries: int = 3, retry_delay: float = 1.0):
        """
        创建数据库表，带重试机制
        
        Args:
            max_retries: 最大重试次数
            retry_delay: 重试延迟（秒）
        """
        import time
        for attempt in range(max_retries):
            try:
                Base.metadata.create_all(bind=self.engine)
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    pass
                else:
                    raise
    
    def get_db(self) -> Session:
        """
        获取数据库会话
        
        Yields:
            Session: 数据库会话
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()
    
    def add_service(self, service_info: dict) -> bool:
        """
        添加服务注册信息
        
        Args:
            service_info: 服务信息字典
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        try:
            db = self.SessionLocal()
            service = ServiceRegistry(**service_info)
            db.add(service)
            db.commit()
            db.refresh(service)
            db.close()
            return True
        except Exception as e:
            self.logger.error(f"添加服务失败: {str(e)}")
            return False
    
    def update_service(self, service_id: str, service_info: dict) -> bool:
        """
        更新服务注册信息
        
        Args:
            service_id: 服务ID
            service_info: 服务信息字典
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            db = self.SessionLocal()
            service = db.query(ServiceRegistry).filter(ServiceRegistry.service_id == service_id).first()
            if not service:
                db.close()
                return False
            
            # 更新服务信息
            for key, value in service_info.items():
                setattr(service, key, value)
            
            db.commit()
            db.close()
            return True
        except Exception as e:
            self.logger.error(f"更新服务失败: {str(e)}")
            return False
    
    def get_service(self, service_id: str) -> ServiceRegistry:
        """
        获取服务注册信息
        
        Args:
            service_id: 服务ID
            
        Returns:
            ServiceRegistry: 服务注册信息对象，未找到返回None
        """
        try:
            db = self.SessionLocal()
            service = db.query(ServiceRegistry).filter(ServiceRegistry.service_id == service_id).first()
            db.close()
            return service
        except Exception as e:
            self.logger.error(f"获取服务失败: {str(e)}")
            return None
    
    def list_services(self, service_type: ServiceType = None, status: ServiceStatus = None) -> list:
        """
        列出所有服务注册信息
        
        Args:
            service_type: 服务类型，可选
            status: 服务状态，可选
            
        Returns:
            list: 服务注册信息列表
        """
        try:
            db = self.SessionLocal()
            query = db.query(ServiceRegistry)
            
            # 按服务类型过滤
            if service_type:
                query = query.filter(ServiceRegistry.service_type == service_type)
            
            # 按状态过滤
            if status:
                query = query.filter(ServiceRegistry.status == status)
            
            services = query.all()
            db.close()
            return services
        except Exception as e:
            self.logger.error(f"列出服务失败: {str(e)}")
            return []
    
    def delete_service(self, service_id: str) -> bool:
        """
        删除服务注册信息
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 删除成功返回True，失败返回False
        """
        try:
            db = self.SessionLocal()
            service = db.query(ServiceRegistry).filter(ServiceRegistry.service_id == service_id).first()
            if not service:
                db.close()
                return False
            
            db.delete(service)
            db.commit()
            db.close()
            return True
        except Exception as e:
            self.logger.error(f"删除服务失败: {str(e)}")
            return False
    
    def update_service_status(self, service_id: str, status: ServiceStatus, reason: str = None) -> bool:
        """
        更新服务状态
        
        Args:
            service_id: 服务ID
            status: 服务状态
            reason: 状态变更原因，可选
            
        Returns:
            bool: 更新成功返回True，失败返回False
        """
        try:
            db = self.SessionLocal()
            service = db.query(ServiceRegistry).filter(ServiceRegistry.service_id == service_id).first()
            if not service:
                db.close()
                return False
            
            service.status = status
            service.reason = reason
            service.last_check_at = datetime.now()
            
            db.commit()
            db.close()
            return True
        except Exception as e:
            self.logger.error(f"更新服务状态失败: {str(e)}")
            return False
    
    def service_exists(self, service_id: str) -> bool:
        """
        检查服务是否已存在
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 存在返回True，不存在返回False
        """
        try:
            db = self.SessionLocal()
            count = db.query(ServiceRegistry).filter(ServiceRegistry.service_id == service_id).count()
            db.close()
            return count > 0
        except Exception as e:
            self.logger.error(f"检查服务存在失败: {str(e)}")
            return False

# 初始化数据库连接
def init_db(db_path: str) -> DatabaseManager:
    """
    初始化数据库连接
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        DatabaseManager: 数据库连接管理器实例
    """
    return DatabaseManager(db_path)
