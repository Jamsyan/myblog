import os
import json

class PathManager:
    """
    文件路径管理类，用于统一管理所有服务和引擎的数据文件路径
    """
    
    def __init__(self, base_path: str):
        """
        初始化文件路径管理器
        
        Args:
            base_path: 项目根目录路径
        """
        self.base_path = base_path
        self.data_dir = os.path.join(base_path, "data")
        
        # 确保数据根目录存在
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
    
    def get_data_dir(self) -> str:
        """
        获取数据根目录路径
        
        Returns:
            str: 数据根目录路径
        """
        return self.data_dir
    
    def get_service_data_dir(self, service_id: str) -> str:
        """
        获取服务数据文件夹路径
        
        Args:
            service_id: 服务ID
            
        Returns:
            str: 服务数据文件夹路径
        """
        # 服务数据存放在data/services目录下
        service_dir = os.path.join(self.data_dir, "services", service_id)
        if not os.path.exists(service_dir):
            os.makedirs(service_dir, exist_ok=True)
        return service_dir
    
    def get_engine_data_dir(self, engine_name: str) -> str:
        """
        获取引擎数据文件夹路径
        
        Args:
            engine_name: 引擎名称
            
        Returns:
            str: 引擎数据文件夹路径
        """
        # 引擎数据存放在data/engine目录下
        engine_dir = os.path.join(self.data_dir, "engine", engine_name)
        if not os.path.exists(engine_dir):
            os.makedirs(engine_dir, exist_ok=True)
        return engine_dir
    
    def get_service_db_path(self, service_id: str, db_name: str = None) -> str:
        """
        获取服务数据库文件路径
        
        Args:
            service_id: 服务ID
            db_name: 数据库名称，默认为service_id
            
        Returns:
            str: 服务数据库文件路径
        """
        if db_name is None:
            db_name = service_id
        service_dir = self.get_service_data_dir(service_id)
        return os.path.join(service_dir, f"{db_name}.db")
    
    def get_engine_db_path(self, engine_name: str, db_name: str = None) -> str:
        """
        获取引擎数据库文件路径
        
        Args:
            engine_name: 引擎名称
            db_name: 数据库名称，默认为engine_name
            
        Returns:
            str: 引擎数据库文件路径
        """
        if db_name is None:
            db_name = engine_name
        engine_dir = self.get_engine_data_dir(engine_name)
        return os.path.join(engine_dir, f"{db_name}.db")
    
    def get_linkgateway_db_path(self, db_name: str = "linkgateway") -> str:
        """
        获取LinkGateway核心数据库文件路径
        
        Args:
            db_name: 数据库名称，默认为linkgateway
            
        Returns:
            str: LinkGateway核心数据库文件路径
        """
        # LinkGateway使用自己独立的数据库文件夹
        lg_dir = os.path.join(self.data_dir, "linkgateway")
        if not os.path.exists(lg_dir):
            os.makedirs(lg_dir, exist_ok=True)
        return os.path.join(lg_dir, f"{db_name}.db")
    
    def get_service_file_path(self, service_id: str, file_name: str) -> str:
        """
        获取服务的文件路径
        
        Args:
            service_id: 服务ID
            file_name: 文件名
            
        Returns:
            str: 服务文件路径
        """
        service_dir = self.get_service_data_dir(service_id)
        return os.path.join(service_dir, file_name)
    
    def get_engine_file_path(self, engine_name: str, file_name: str) -> str:
        """
        获取引擎的文件路径
        
        Args:
            engine_name: 引擎名称
            file_name: 文件名
            
        Returns:
            str: 引擎文件路径
        """
        engine_dir = self.get_engine_data_dir(engine_name)
        return os.path.join(engine_dir, file_name)
    
    def get_file_path(self, relative_path: str) -> str:
        """
        获取相对路径对应的绝对路径
        
        Args:
            relative_path: 相对路径
            
        Returns:
            str: 绝对路径
        """
        if os.path.isabs(relative_path):
            return relative_path
        return os.path.join(self.base_path, relative_path)
    
    def validate_path(self, path: str) -> bool:
        """
        验证路径是否在数据目录范围内，防止路径遍历攻击
        
        Args:
            path: 要验证的路径
            
        Returns:
            bool: 路径有效返回True，无效返回False
        """
        # 获取绝对路径
        abs_path = os.path.abspath(path)
        # 检查路径是否在数据目录范围内
        return abs_path.startswith(os.path.abspath(self.data_dir))
    
    def clean_path(self, path: str) -> str:
        """
        清理路径，确保路径在数据目录范围内
        
        Args:
            path: 要清理的路径
            
        Returns:
            str: 清理后的路径
        """
        # 如果是相对路径，直接拼接数据目录
        if not os.path.isabs(path):
            return os.path.join(self.data_dir, path)
        
        # 如果是绝对路径且在数据目录范围内，直接返回
        if path.startswith(self.data_dir):
            return path
        
        # 绝对路径但不在数据目录范围内，转换为相对路径
        rel_path = os.path.relpath(path, self.data_dir)
        
        # 如果是上一级目录，直接使用文件名
        if rel_path.startswith(".."):
            return os.path.join(self.data_dir, os.path.basename(path))
        
        return os.path.join(self.data_dir, rel_path)
    
    def get_service_config_path(self, service_id: str, config_name: str = "service.json") -> str:
        """
        获取服务配置文件路径
        
        Args:
            service_id: 服务ID
            config_name: 配置文件名，默认为service.json
            
        Returns:
            str: 服务配置文件路径
        """
        return os.path.join(self.base_path, "services", service_id, config_name)
    
    def get_engine_config_path(self, engine_name: str, config_name: str = "engine.json") -> str:
        """
        获取引擎配置文件路径
        
        Args:
            engine_name: 引擎名称
            config_name: 配置文件名，默认为engine.json
            
        Returns:
            str: 引擎配置文件路径
        """
        return os.path.join(self.base_path, "engines", f"{engine_name}.json")
    
    def get_service_json_path(self, service_path: str) -> str:
        """
        获取服务的service.json文件路径
        
        Args:
            service_path: 服务文件夹路径
            
        Returns:
            str: service.json文件路径
        """
        return os.path.join(service_path, "service.json")
    
    def get_engine_json_path(self, engine_path: str) -> str:
        """
        获取引擎的engine.json文件路径
        
        Args:
            engine_path: 引擎文件夹路径或文件路径
            
        Returns:
            str: engine.json文件路径
        """
        # 如果是文件路径，获取其所在目录
        if os.path.isfile(engine_path):
            engine_dir = os.path.dirname(engine_path)
            engine_name = os.path.splitext(os.path.basename(engine_path))[0]
        else:
            engine_dir = engine_path
            engine_name = os.path.basename(engine_path)
        
        # 检查引擎目录下是否有engine.json文件
        engine_json_path = os.path.join(engine_dir, "engine.json")
        if os.path.exists(engine_json_path):
            return engine_json_path
        
        # 检查引擎文件同级目录下是否有同名的json文件
        engine_json_path = os.path.join(engine_dir, f"{engine_name}.json")
        return engine_json_path
    
    def load_json_file(self, file_path: str) -> dict:
        """
        加载JSON文件
        
        Args:
            file_path: JSON文件路径
            
        Returns:
            dict: JSON文件内容
        """
        if not os.path.exists(file_path):
            return {}
        
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def save_json_file(self, file_path: str, data: dict) -> bool:
        """
        保存JSON文件
        
        Args:
            file_path: JSON文件路径
            data: 要保存的数据
            
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            # 确保父目录存在
            parent_dir = os.path.dirname(file_path)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save JSON file: {str(e)}")
            return False
    
    def get_log_root_dir(self) -> str:
        """
        获取日志根目录路径
        
        Returns:
            str: 日志根目录路径
        """
        log_dir = os.path.join(self.base_path, "log")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    def get_linkgateway_log_path(self, log_name: str = "linkgateway") -> str:
        """
        获取LinkGateway日志文件路径
        
        Args:
            log_name: 日志文件名，默认为linkgateway
            
        Returns:
            str: LinkGateway日志文件路径
        """
        lg_log_dir = os.path.join(self.get_log_root_dir(), "linkgateway")
        if not os.path.exists(lg_log_dir):
            os.makedirs(lg_log_dir, exist_ok=True)
        return os.path.join(lg_log_dir, log_name)
    
    def get_engine_log_path(self, engine_name: str, log_name: str = None) -> str:
        """
        获取引擎日志文件路径
        
        Args:
            engine_name: 引擎名称
            log_name: 日志文件名，默认为引擎名称
            
        Returns:
            str: 引擎日志文件路径
        """
        if log_name is None:
            log_name = engine_name
        engine_log_dir = os.path.join(self.get_log_root_dir(), "engines", engine_name)
        if not os.path.exists(engine_log_dir):
            os.makedirs(engine_log_dir, exist_ok=True)
        return os.path.join(engine_log_dir, log_name)
    
    def get_service_log_path(self, service_name: str, log_name: str = None) -> str:
        """
        获取服务日志文件路径
        
        Args:
            service_name: 服务名称
            log_name: 日志文件名，默认为服务名称
            
        Returns:
            str: 服务日志文件路径
        """
        if log_name is None:
            log_name = service_name
        service_log_dir = os.path.join(self.get_log_root_dir(), "services", service_name)
        if not os.path.exists(service_log_dir):
            os.makedirs(service_log_dir, exist_ok=True)
        return os.path.join(service_log_dir, log_name)
