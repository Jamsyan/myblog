import os
import sqlite3
from typing import Dict, Any, Optional, List
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlalchemy.pool import QueuePool
from .path_manager import PathManager
from .logs import get_logger

class DatabaseLinkManager:
    """
    数据库链接管理类，负责管理所有业务服务的数据库连接
    """
    
    def __init__(self, base_path: str):
        """
        初始化数据库链接管理器
        
        Args:
            base_path: 项目根目录路径
        """
        self.base_path = base_path
        self.connections: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Session] = {}
        self.Base = declarative_base()
        
        # 初始化路径管理器
        self.path_manager = PathManager(base_path)
        
        # 初始化日志
        self.logger = get_logger("DatabaseLinkManager")
        self.logger.info("数据库链接管理器初始化成功")
    
    def create_connection(self, service_id: str, db_config: Dict[str, Any]) -> bool:
        """
        创建数据库连接
        
        Args:
            service_id: 服务ID
            db_config: 数据库配置
            
        Returns:
            bool: 连接成功返回True，失败返回False
        """
        if not self._validate_connection_params(service_id, db_config):
            return False
        
        db_type = db_config.get("type")
        
        if db_type == "sqlite":
            return self._create_sqlite_connection(service_id, db_config)
        elif db_type in ["mysql", "postgresql"]:
            return self._create_server_connection(service_id, db_config, db_type)
        else:
            self.logger.error(f"不支持的数据库类型: {db_type}")
            return False
    
    def _validate_connection_params(self, service_id: str, db_config: Dict[str, Any]) -> bool:
        """
        验证连接参数
        
        Args:
            service_id: 服务ID
            db_config: 数据库配置
            
        Returns:
            bool: 验证通过返回True
        """
        if not service_id:
            self.logger.error("服务ID不能为空")
            return False
        
        if not isinstance(db_config, dict):
            self.logger.error("数据库配置必须是字典类型")
            return False
        
        db_type = db_config.get("type")
        if not db_type:
            self.logger.error("未指定数据库类型")
            return False
        
        return True
    
    def _create_sqlite_connection(self, service_id: str, db_config: Dict[str, Any]) -> bool:
        """
        创建SQLite数据库连接
        
        Args:
            service_id: 服务ID
            db_config: 数据库配置
            
        Returns:
            bool: 连接成功返回True，失败返回False
        """
        db_name = db_config.get("name", service_id)
        db_path = self.path_manager.get_service_db_path(service_id, db_name)
        
        db_dir = os.path.dirname(db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
        
        engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True
        )
        
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        self.connections[service_id] = {
            "engine": engine,
            "SessionLocal": SessionLocal,
            "db_type": "sqlite",
            "db_path": db_path
        }
        
        self.logger.debug(f"为服务 {service_id} 创建了SQLite连接，路径：{db_path}")
        return True
    
    def _create_server_connection(self, service_id: str, db_config: Dict[str, Any], db_type: str) -> bool:
        """
        创建服务器数据库连接（MySQL或PostgreSQL）
        
        Args:
            service_id: 服务ID
            db_config: 数据库配置
            db_type: 数据库类型
            
        Returns:
            bool: 连接成功返回True，失败返回False
        """
        host = db_config.get("host", "localhost")
        port = db_config.get("port")
        username = db_config.get("username")
        password = db_config.get("password")
        database = db_config.get("database")
        
        if not all([host, port, username, password, database]):
            self.logger.error(f"服务 {service_id} 的数据库配置不完整")
            return False
        
        url = self._build_connection_url(db_type, username, password, host, port, database)
        
        if not self._test_server_connection(service_id, url):
            return False
        
        engine = self._create_server_engine(url, db_type)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        self.connections[service_id] = {
            "engine": engine,
            "SessionLocal": SessionLocal,
            "db_type": db_type,
            "host": host,
            "port": port,
            "database": database
        }
        
        self.logger.debug(f"为服务 {service_id} 创建了{db_type}连接，地址：{host}:{port}/{database}")
        return True
    
    def _build_connection_url(self, db_type: str, username: str, password: str, host: str, port: int, database: str) -> str:
        """
        构建数据库连接URL
        
        Args:
            db_type: 数据库类型
            username: 用户名
            password: 密码
            host: 主机
            port: 端口
            database: 数据库名
            
        Returns:
            str: 连接URL
        """
        if db_type == "mysql":
            return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"
        else:
            return f"postgresql://{username}:{password}@{host}:{port}/{database}"
    
    def _test_server_connection(self, service_id: str, url: str) -> bool:
        """
        测试服务器数据库连接
        
        Args:
            service_id: 服务ID
            url: 连接URL
            
        Returns:
            bool: 测试成功返回True
        """
        engine = create_engine(
            url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
        
        try:
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.error(f"服务 {service_id} 的数据库连接测试失败: {str(e)}")
            return False
    
    def _create_server_engine(self, url: str, db_type: str):
        """
        创建服务器数据库引擎
        
        Args:
            url: 连接URL
            db_type: 数据库类型
            
        Returns:
            Engine: SQLAlchemy引擎
        """
        return create_engine(
            url,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600
        )
    
    def get_connection(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        获取数据库连接
        
        Args:
            service_id: 服务ID
            
        Returns:
            Optional[Dict[str, Any]]: 连接信息，未找到返回None
        """
        return self.connections.get(service_id)
    
    def get_session(self, service_id: str) -> Optional[Session]:
        """
        获取数据库会话
        
        Args:
            service_id: 服务ID
            
        Returns:
            Optional[Session]: 数据库会话，未找到返回None
        """
        if not service_id:
            self.logger.error("服务ID不能为空")
            return None
        
        if self._reuse_existing_session(service_id):
            return self.sessions[service_id]
        
        connection = self.get_connection(service_id)
        if not connection:
            self.logger.error(f"服务 {service_id} 的连接未找到")
            return None
        
        return self._create_new_session(service_id, connection)
    
    def _reuse_existing_session(self, service_id: str) -> bool:
        """
        重用现有会话
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 成功重用返回True
        """
        if service_id not in self.sessions:
            return False
        
        session = self.sessions[service_id]
        try:
            session.execute("SELECT 1")
            return True
        except Exception as e:
            self.logger.warning(f"会话无效，创建新会话: {str(e)}")
            self.close_session(service_id)
            return False
    
    def _create_new_session(self, service_id: str, connection: Dict[str, Any]) -> Optional[Session]:
        """
        创建新会话
        
        Args:
            service_id: 服务ID
            connection: 连接信息
            
        Returns:
            Optional[Session]: 新会话，失败返回None
        """
        SessionLocal = connection.get("SessionLocal")
        if not SessionLocal:
            self.logger.error(f"服务 {service_id} 的SessionLocal未找到")
            return None
        
        session = SessionLocal()
        self.sessions[service_id] = session
        self.logger.debug(f"为服务 {service_id} 创建了新的数据库会话")
        return session
    
    def close_session(self, service_id: str) -> bool:
        """
        关闭数据库会话
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 关闭成功返回True，失败返回False
        """
        try:
            if service_id in self.sessions:
                session = self.sessions[service_id]
                try:
                    session.close()
                except Exception as e:
                    self.logger.warning(f"关闭会话时出错: {str(e)}")
                del self.sessions[service_id]
                self.logger.debug(f"已关闭服务 {service_id} 的数据库会话")
            return True
        except Exception as e:
            self.logger.error(f"关闭服务 {service_id} 的会话失败: {str(e)}")
            return False
    
    def close_all_sessions(self) -> bool:
        """
        关闭所有数据库会话
        
        Returns:
            bool: 关闭成功返回True，失败返回False
        """
        try:
            session_count = len(self.sessions)
            for service_id in list(self.sessions.keys()):
                self.close_session(service_id)
            self.logger.debug(f"已关闭所有 {session_count} 个数据库会话")
            return True
        except Exception as e:
            self.logger.error(f"关闭所有会话失败: {str(e)}")
            return False
    
    def disconnect(self, service_id: str) -> bool:
        """
        断开数据库连接
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 断开成功返回True，失败返回False
        """
        try:
            # 验证参数
            if not service_id:
                self.logger.error("服务ID不能为空")
                return False
            
            # 关闭会话
            self.close_session(service_id)
            
            # 移除连接
            if service_id in self.connections:
                # 尝试关闭引擎
                connection = self.connections[service_id]
                engine = connection.get("engine")
                if engine:
                    try:
                        engine.dispose()
                        self.logger.debug(f"已释放服务 {service_id} 的引擎")
                    except Exception as e:
                        self.logger.warning(f"释放引擎时出错: {str(e)}")
                del self.connections[service_id]
                self.logger.info(f"已断开服务 {service_id} 的数据库连接")
            
            return True
        except Exception as e:
            self.logger.error(f"断开服务 {service_id} 的数据库连接失败: {str(e)}")
            return False
    
    def disconnect_all(self) -> bool:
        """
        断开所有数据库连接
        
        Returns:
            bool: 断开成功返回True，失败返回False
        """
        try:
            # 关闭所有会话
            self.close_all_sessions()
            
            # 清空连接并释放资源
            connection_count = len(self.connections)
            for service_id, connection in list(self.connections.items()):
                engine = connection.get("engine")
                if engine:
                    try:
                        engine.dispose()
                    except Exception as e:
                        self.logger.warning(f"释放服务 {service_id} 的引擎时出错: {str(e)}")
            
            self.connections.clear()
            self.logger.info(f"已断开所有 {connection_count} 个数据库连接")
            
            return True
        except Exception as e:
            self.logger.error(f"断开所有数据库连接失败: {str(e)}")
            return False
    
    def init_database(self, service_id: str, models: List[Any]) -> bool:
        """
        初始化数据库，创建所有表
        
        Args:
            service_id: 服务ID
            models: 模型类列表
            
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        try:
            # 验证参数
            if not service_id:
                self.logger.error("服务ID不能为空")
                return False
            
            if not isinstance(models, list):
                self.logger.error("模型必须是列表类型")
                return False
            
            connection = self.get_connection(service_id)
            if not connection:
                self.logger.error(f"服务 {service_id} 的连接未找到")
                return False
            
            engine = connection["engine"]
            
            # 为每个模型添加到Base.metadata
            for model in models:
                if hasattr(model, "__table__"):
                    model.__table__.metadata = self.Base.metadata
            
            # 创建所有表
            self.Base.metadata.create_all(bind=engine)
            
            self.logger.info(f"已初始化服务 {service_id} 的数据库，创建了 {len(self.Base.metadata.tables)} 个表")
            return True
        except Exception as e:
            self.logger.error(f"初始化服务 {service_id} 的数据库失败: {str(e)}")
            return False
    
    def get_db(self, service_id: str):
        """
        获取数据库会话的依赖函数，用于FastAPI路由
        
        Args:
            service_id: 服务ID
            
        Yields:
            Session: 数据库会话
        """
        db = self.get_session(service_id)
        if not db:
            raise Exception(f"服务 {service_id} 的数据库会话未找到")
        
        try:
            yield db
        finally:
            self.close_session(service_id)
    
    def test_connection(self, service_id: str) -> bool:
        """
        测试数据库连接
        
        Args:
            service_id: 服务ID
            
        Returns:
            bool: 连接正常返回True，异常返回False
        """
        try:
            # 验证参数
            if not service_id:
                self.logger.error("服务ID不能为空")
                return False
            
            connection = self.get_connection(service_id)
            if not connection:
                self.logger.error(f"服务 {service_id} 的连接未找到")
                return False
            
            engine = connection["engine"]
            
            # 测试连接
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            
            self.logger.debug(f"服务 {service_id} 的数据库连接测试通过")
            return True
        except Exception as e:
            self.logger.error(f"服务 {service_id} 的数据库连接测试失败: {str(e)}")
            return False
