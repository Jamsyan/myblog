import uuid
import os
import inspect
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List

class BaseEngine(ABC):
    """
    引擎基类，所有引擎必须继承此基类
    """
    
    # 引擎状态枚举
    class Status:
        STOPPED = "stopped"
        STARTING = "starting"
        RUNNING = "running"
        STOPPING = "stopping"
        ERROR = "error"
    
    # 引擎类型枚举
    class EngineType:
        KERNEL = "kernel"
        NETWORK = "network"
    
    def __init__(self, service_name: str, version: str, engine_type: str = "kernel"):
        """
        初始化引擎
        
        Args:
            service_name: 服务名称
            version: 服务版本
            engine_type: 引擎类型（"kernel" 或 "network"）
        """
        self.service_id = str(uuid.uuid4())
        self.service_name = service_name
        self.version = version
        self.engine_type = engine_type
        self.status = self.Status.STOPPED
        self.error_message = None
        
        # 标记是否允许直接调用（仅 LinkGateway 可以设置为 True）
        self._allow_direct_call = False
        
        # 获取项目根目录的绝对路径
        current_path = os.path.abspath(__file__)
        # 向上遍历，找到项目根目录（包含main.py的目录）
        self.project_root = os.path.dirname(os.path.dirname(current_path))
        
        # 引擎配置
        self.config = {}
    
    def get_data_dir(self) -> str:
        """
        获取引擎数据目录路径
        
        Returns:
            str: 数据目录的绝对路径
        """
        # 引擎数据统一存储在data/engine目录下
        data_dir = os.path.join(self.project_root, "data", "engine", self.service_name)
        # 确保数据目录存在
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def get_db_path(self) -> str:
        """
        获取引擎数据库文件路径
        
        Returns:
            str: 数据库文件的绝对路径
        """
        data_dir = self.get_data_dir()
        return os.path.join(data_dir, f"{self.service_name}.db")
    
    def get_log_dir(self) -> str:
        """
        获取引擎日志目录路径
        
        Returns:
            str: 日志目录的绝对路径
        """
        log_dir = os.path.join(self.project_root, "logs", "engine", self.service_name)
        os.makedirs(log_dir, exist_ok=True)
        return log_dir
    
    def load_config(self, config: Dict[str, Any]) -> None:
        """
        加载引擎配置
        
        Args:
            config: 配置数据
        """
        self.config.update(config)
    
    def get_config(self) -> Dict[str, Any]:
        """
        获取引擎配置
        
        Returns:
            Dict[str, Any]: 引擎配置
        """
        return self.config
    
    @abstractmethod
    def start(self) -> bool:
        """
        启动引擎
        
        Returns:
            bool: 启动成功返回True，失败返回False
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        停止引擎
        
        Returns:
            bool: 停止成功返回True，失败返回False
        """
        pass
    
    @abstractmethod
    def handle_request(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理请求（带调用者验证）
        
        Args:
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 验证调用者
        if not self._validate_caller():
            raise PermissionError(
                f"非法调用引擎 {self.service_id}！"
                f"请通过 LinkGateway 的内部通信机制调用。"
            )
        # 调用实际的请求处理逻辑
        return self._handle_request_impl(action, data)
    
    @abstractmethod
    def _handle_request_impl(self, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        实际的请求处理逻辑（子类实现）
        
        Args:
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        pass
    
    def _validate_caller(self) -> bool:
        """
        验证调用者是否合法
        
        Returns:
            bool: 合法返回 True，否则返回 False
        """
        # 获取调用栈
        stack = inspect.stack()
        
        # 检查调用栈中是否包含 LinkGateway
        for frame_info in stack:
            # frame_info.frame.f_code.co_filename 是调用文件路径
            filename = frame_info.filename
            # frame_info.frame.f_code.co_name 是函数名
            func_name = frame_info.function
            
            # 检查是否从 LinkGateway 调用
            if "LinkGateway" in filename or "gateway.py" in filename:
                # 进一步检查是否从合法方法调用
                if func_name in ["forward_request", "send_request", "proxy_request", "send_async_request"]:
                    return True
        
        # 如果允许直接调用（用于测试），返回 True
        if self._allow_direct_call:
            return True
        
        # 调用者不合法
        return False
    
    @abstractmethod
    def get_api_routes(self) -> List[Dict[str, Any]]:
        """
        获取引擎的API路由定义
        
        Returns:
            List[Dict[str, Any]]: API路由定义列表
        """
        pass
    
    @abstractmethod
    def get_dependencies(self) -> List[str]:
        """
        获取引擎依赖的其他服务
        
        Returns:
            List[str]: 依赖服务列表
        """
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        健康检查
        
        Returns:
            Dict[str, Any]: 健康检查结果
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        获取引擎元数据
        
        Returns:
            Dict[str, Any]: 引擎元数据
        """
        return {
            "service_id": self.service_id,
            "service_name": self.service_name,
            "version": self.version,
            "engine_type": self.engine_type,
            "status": self.status,
            "error_message": self.error_message,
            "config": self.config
        }
    
    def set_status(self, status: str, error_message: Optional[str] = None) -> None:
        """
        设置引擎状态
        
        Args:
            status: 状态
            error_message: 错误信息（可选）
        """
        self.status = status
        self.error_message = error_message
    
    def is_compatible(self, min_version: str) -> bool:
        """
        检查版本兼容性
        
        Args:
            min_version: 最低兼容版本
            
        Returns:
            bool: 兼容返回True，否则返回False
        """
        try:
            current_version = list(map(int, self.version.split('.')))
            required_version = list(map(int, min_version.split('.')))
            
            for i in range(max(len(current_version), len(required_version))):
                current = current_version[i] if i < len(current_version) else 0
                required = required_version[i] if i < len(required_version) else 0
                
                if current > required:
                    return True
                elif current < required:
                    return False
            
            return True
        except:
            return False
    
    def validate_config(self) -> bool:
        """
        验证引擎配置
        
        Returns:
            bool: 配置有效返回True，否则返回False
        """
        # 基础配置验证
        required_fields = ["service_name", "version", "engine_type"]
        for field in required_fields:
            if not getattr(self, field, None):
                return False
        
        # 引擎类型验证
        valid_engine_types = [self.EngineType.KERNEL, self.EngineType.NETWORK]
        if self.engine_type not in valid_engine_types:
            return False
        
        return True
