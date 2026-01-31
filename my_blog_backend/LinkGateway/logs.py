import os
import sys
import logging
import csv
from logging.handlers import TimedRotatingFileHandler
import datetime
import uuid
from enum import Enum
from typing import Optional, Dict, Any

try:
    from colorama import init
    init()
except ImportError:
    pass

# 日志级别枚举
class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# 日志颜色配置
class LogColor:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    # 日志级别对应的颜色
    LEVEL_COLORS = {
        "DEBUG": GREEN,
        "INFO": CYAN,
        "WARNING": YELLOW,
        "ERROR": RED,
        "CRITICAL": MAGENTA
    }


class CSVLogHandler(logging.Handler):
    """
    CSV 格式的日志处理器，将日志以表格形式存储
    统一存储到 log/logs.csv
    """
    
    def __init__(self, filename: str, encoding: str = "utf-8"):
        """
        初始化 CSV 日志处理器
        
        Args:
            filename: CSV 文件路径
            encoding: 文件编码
        """
        super().__init__()
        self.filename = filename
        self.encoding = encoding
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        """
        确保 CSV 文件存在并写入表头
        """
        if not os.path.exists(self.filename):
            # 确保目录存在
            log_dir = os.path.dirname(self.filename)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
            
            # 写入表头
            with open(self.filename, 'w', encoding=self.encoding, newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['时间戳', '日志级别', '服务ID', '请求ID', '模块名', '消息'])
    
    def emit(self, record: logging.LogRecord):
        """
        发送日志记录到 CSV 文件
        保留完整日志消息，不截断
        
        Args:
            record: 日志记录对象
        """
        try:
            # 提取日志信息
            timestamp = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            levelname = record.levelname
            service_id = getattr(record, 'service_id', 'unknown')
            request_id = getattr(record, 'request_id', str(uuid.uuid4())[:8])
            name = record.name
            message = record.getMessage()
            
            # 写入 CSV 文件，保留完整消息
            with open(self.filename, 'a', encoding=self.encoding, newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, levelname, service_id, request_id, name, message])
        except Exception:
            self.handleError(record)


class Logger:
    """
    日志工具类，实现彩色日志输出和日志滚动功能
    控制台输出智能截断，文件和CSV输出保留完整信息
    """
    
    # 存储已初始化的logger名称，避免重复创建处理器
    initialized_loggers = set()
    
    # 控制台日志最大长度
    CONSOLE_MAX_LENGTH = 100
    
    @staticmethod
    def _truncate_message(message: str, max_length: int = None) -> str:
        """
        智能截断日志消息，保留关键信息
        
        Args:
            message: 原始消息
            max_length: 最大长度，默认使用类定义的CONSOLE_MAX_LENGTH
            
        Returns:
            str: 截断后的消息
        """
        if max_length is None:
            max_length = Logger.CONSOLE_MAX_LENGTH
        
        if len(message) <= max_length:
            return message
        
        # 智能截断：优先保留ID、状态等关键信息
        # 尝试保留最后的部分（通常是关键信息）
        truncated = message[:max_length - 3] + "..."
        return truncated
    
    def __init__(self, name: str = "LinkGateway", log_file: Optional[str] = None, log_type: str = "linkgateway"):
        """
        初始化日志工具
        
        Args:
            name: 日志名称
            log_file: 日志文件路径，None表示只输出到控制台
            log_type: 日志类型，linkgateway或engine
        """
        self.name = name
        self.log_file = log_file
        self.log_type = log_type
        
        self.is_structured_output_enabled = False
        self.collected_logs = {
            'plugins': {'success': [], 'failed': [], 'details': []},
            'services': {'success': [], 'failed': [], 'details': []},
            'apis': {'success': [], 'failed': [], 'details': []},
            'warnings': [],
            'errors': []
        }
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # 禁用日志传播，避免父logger处理
        self.logger.propagate = False
        
        # 检查是否已经初始化过，避免重复添加处理器
        if name not in Logger.initialized_loggers:
            # 移除默认的处理器
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
            
            # 配置控制台处理器，明确指定输出到stdout并强制刷新
            console_handler = logging.StreamHandler(stream=sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(self._get_console_formatter())
            self.logger.addHandler(console_handler)
            
            # 配置文件处理器（如果指定了日志文件）
            if log_file:
                # 确保日志文件目录存在
                log_dir = os.path.dirname(log_file)
                if log_dir and not os.path.exists(log_dir):
                    os.makedirs(log_dir, exist_ok=True)
                
                # 为不同级别配置不同的日志处理器
                self._configure_file_handlers(log_file)
            
            # 标记为已初始化
            Logger.initialized_loggers.add(name)
    
    def _get_console_formatter(self) -> logging.Formatter:
        """
        获取控制台日志格式化器
        控制台输出智能截断，避免换行
        
        Returns:
            logging.Formatter: 控制台日志格式化器
        """
        class StructuredFormatter(logging.Formatter):
            """
            结构化日志格式化器，实现固定宽度的列对齐格式
            格式：[等级] [组件名] - 操作描述 [状态]
            """
            
            def __init__(self):
                super().__init__()
                self.level_width = 8
                self.name_width = 20
                self.desc_width = 50
                self.status_width = 10
            
            def format(self, record):
                levelname = record.levelname
                name = record.name
                message = record.getMessage()
                
                level_color = LogColor.LEVEL_COLORS.get(levelname, LogColor.WHITE)
                
                level_display = f"{levelname.ljust(self.level_width)}:"
                colored_level = f"{level_color}{level_display}{LogColor.RESET}"
                
                name_display = f"{name.ljust(self.name_width)}"
                
                status = getattr(record, 'status', None)
                if status:
                    status_color = LogColor.GREEN if status == '成功' else LogColor.RED
                    status_display = f"[{status_color}{status}{LogColor.RESET}]"
                else:
                    status_display = ""
                
                formatted_message = f"{colored_level}{name_display} | {message.ljust(self.desc_width)} {status_display}"
                
                return formatted_message
        
        return StructuredFormatter()
    
    def _get_file_formatter(self) -> logging.Formatter:
        """
        获取文件日志格式化器
        
        Returns:
            logging.Formatter: 文件日志格式化器
        """
        class EnhancedFormatter(logging.Formatter):
            def format(self, record):
                # 确保record有request_id属性
                if not hasattr(record, 'request_id'):
                    record.request_id = str(uuid.uuid4())[:8]
                
                # 确保record有service_id属性
                if not hasattr(record, 'service_id'):
                    record.service_id = 'unknown'
                
                # 格式化日志
                log_format = "%(asctime)s [%(levelname)s:] [%(service_id)s] [%(request_id)s] %(name)s | %(message)s"
                formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
                return formatter.format(record)
        
        return EnhancedFormatter()
    
    def _configure_file_handlers(self, base_log_file: str) -> None:
        """
        为不同级别配置不同的日志处理器
        CSV文件统一存储到 log/logs.csv
        
        Args:
            base_log_file: 基础日志文件路径
        """
        try:
            self._add_debug_info_handler(base_log_file)
            self._add_warning_handler(base_log_file)
            self._add_error_critical_handler(base_log_file)
            self._add_csv_handler()
        except Exception as e:
            print(f"Warning: Failed to initialize file log handlers: {str(e)}")
    
    def _add_debug_info_handler(self, base_log_file: str) -> None:
        """
        添加DEBUG和INFO级别处理器
        
        Args:
            base_log_file: 基础日志文件路径
        """
        debug_info_handler = TimedRotatingFileHandler(
            filename=f"{base_log_file}.debug_info",
            when="H",
            interval=1,
            backupCount=24,
            encoding="utf-8",
            delay=True
        )
        debug_info_handler.setLevel(logging.DEBUG)
        debug_info_handler.setFormatter(self._get_file_formatter())
        debug_info_handler.addFilter(lambda record: record.levelno in (logging.DEBUG, logging.INFO))
        self.logger.addHandler(debug_info_handler)
    
    def _add_warning_handler(self, base_log_file: str) -> None:
        """
        添加WARNING级别处理器
        
        Args:
            base_log_file: 基础日志文件路径
        """
        warning_handler = TimedRotatingFileHandler(
            filename=f"{base_log_file}.warning",
            when="D",
            interval=1,
            backupCount=3,
            encoding="utf-8",
            delay=True
        )
        warning_handler.setLevel(logging.WARNING)
        warning_handler.setFormatter(self._get_file_formatter())
        warning_handler.addFilter(lambda record: record.levelno == logging.WARNING)
        self.logger.addHandler(warning_handler)
    
    def _add_error_critical_handler(self, base_log_file: str) -> None:
        """
        添加ERROR和CRITICAL级别处理器
        
        Args:
            base_log_file: 基础日志文件路径
        """
        error_critical_handler = TimedRotatingFileHandler(
            filename=f"{base_log_file}.error",
            when="D",
            interval=1,
            backupCount=14,
            encoding="utf-8",
            delay=True
        )
        error_critical_handler.setLevel(logging.ERROR)
        error_critical_handler.setFormatter(self._get_file_formatter())
        error_critical_handler.addFilter(lambda record: record.levelno in (logging.ERROR, logging.CRITICAL))
        self.logger.addHandler(error_critical_handler)
    
    def _add_csv_handler(self) -> None:
        """
        添加CSV文件处理器
        """
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_log_file = os.path.join(project_root, "log", "logs.csv")
        csv_handler = CSVLogHandler(
            filename=csv_log_file,
            encoding="utf-8"
        )
        csv_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(csv_handler)
    
    def debug(self, message: str, **kwargs) -> None:
        """
        输出调试级别的日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志参数
        """
        self._log(LogLevel.DEBUG.value, message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        """
        输出信息级别的日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志参数
        """
        self._log(LogLevel.INFO.value, message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        """
        输出警告级别的日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志参数
        """
        self._log(LogLevel.WARNING.value, message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        """
        输出错误级别的日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志参数
        """
        self._log(LogLevel.ERROR.value, message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        """
        输出严重级别的日志
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志参数
        """
        self._log(LogLevel.CRITICAL.value, message, **kwargs)
    
    def _log(self, level: str, message: str, **kwargs) -> None:
        """
        输出日志
        
        Args:
            level: 日志级别（英文）
            message: 日志消息
            **kwargs: 额外的日志参数，包括request_id、service_id和status（布尔值）
        """
        request_id = kwargs.pop('request_id', str(uuid.uuid4())[:8])
        service_id = kwargs.pop('service_id', self.log_type)
        status = kwargs.pop('status', None)
        
        if kwargs:
            extra_info = " ".join([f"{k}={v}" for k, v in kwargs.items()])
            message = f"{message} {extra_info}"
        
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
        extra = {
            'request_id': request_id,
            'service_id': service_id
        }
        
        if status is True:
            extra['status'] = '成功'
        elif status is False:
            extra['status'] = '失败'
        
        if self.is_structured_output_enabled:
            return
        
        self.logger.log(level_map[level], message, extra=extra)
    
    def log(self, level: str, message: str, status: bool = None, **kwargs) -> None:
        """
        统一的日志输出方法
        
        Args:
            level: 日志级别（INFO、ERROR、DEBUG、WARNING、CRITICAL）
            message: 日志消息
            status: 状态（True=成功，False=失败，None=无状态）
            **kwargs: 额外的日志参数
        """
        self._log(level, message, status=status, **kwargs)
    
    def log_success(self, message: str, **kwargs) -> None:
        """
        输出成功日志，自动添加绿色[成功]状态
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志参数
        """
        self.log("INFO", message, True, **kwargs)
    
    def log_failure(self, message: str, **kwargs) -> None:
        """
        输出失败日志，自动添加红色[失败]状态
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志参数
        """
        self.log("ERROR", message, False, **kwargs)
    
    def log_progress(self, message: str, **kwargs) -> None:
        """
        输出进度日志，不带状态
        
        Args:
            message: 日志消息
            **kwargs: 额外的日志参数
        """
        self.log("INFO", message, None, **kwargs)
    
    def enable_structured_output(self) -> None:
        """
        启用结构化输出模式
        """
        self.is_structured_output_enabled = True
        self._clear_collected_logs()
    
    def disable_structured_output(self) -> None:
        """
        禁用结构化输出模式
        """
        self.is_structured_output_enabled = False
        self._clear_collected_logs()
    
    def _clear_collected_logs(self) -> None:
        """
        清空收集的日志
        """
        self.collected_logs = {
            'plugins': {'success': [], 'failed': [], 'details': []},
            'services': {'success': [], 'failed': [], 'details': []},
            'apis': {'success': [], 'failed': [], 'details': []},
            'warnings': [],
            'errors': []
        }
    
    def collect_plugin(self, plugin_name: str, status: bool, detail: str = None) -> None:
        """
        收集插件信息
        
        Args:
            plugin_name: 插件名称
            status: 状态（True=成功，False=失败）
            detail: 详细信息（可选）
        """
        if not self.is_structured_output_enabled:
            return
        
        if status:
            self.collected_logs['plugins']['success'].append(plugin_name)
        else:
            self.collected_logs['plugins']['failed'].append(plugin_name)
        
        if detail:
            self.collected_logs['plugins']['details'].append(detail)
    
    def collect_service(self, service_name: str, status: bool, detail: str = None) -> None:
        """
        收集服务信息
        
        Args:
            service_name: 服务名称
            status: 状态（True=成功，False=失败）
            detail: 详细信息（可选）
        """
        if not self.is_structured_output_enabled:
            return
        
        if status:
            self.collected_logs['services']['success'].append(service_name)
        else:
            self.collected_logs['services']['failed'].append(service_name)
        
        if detail:
            self.collected_logs['services']['details'].append(detail)
    
    def collect_api(self, api_name: str, status: bool, detail: str = None) -> None:
        """
        收集API信息
        
        Args:
            api_name: API名称
            status: 状态（True=成功，False=失败）
            detail: 详细信息（可选）
        """
        if not self.is_structured_output_enabled:
            return
        
        if status:
            self.collected_logs['apis']['success'].append(api_name)
        else:
            self.collected_logs['apis']['failed'].append(api_name)
        
        if detail:
            self.collected_logs['apis']['details'].append(detail)
    
    def collect_warning(self, message: str) -> None:
        """
        收集警告信息
        
        Args:
            message: 警告消息
        """
        if not self.is_structured_output_enabled:
            return
        
        self.collected_logs['warnings'].append(message)
    
    def collect_error(self, message: str) -> None:
        """
        收集错误信息
        
        Args:
            message: 错误消息
        """
        if not self.is_structured_output_enabled:
            return
        
        self.collected_logs['errors'].append(message)
    
    def output_collected_logs(self) -> None:
        """
        输出所有收集的日志信息，使用rich.tree.Tree实现专业的树状图格式
        """
        if not self.is_structured_output_enabled:
            return
        
        self.log("INFO", "初始化核心组件", True)
        
        if self.collected_logs['plugins']['success'] or self.collected_logs['plugins']['failed']:
            self.log("INFO", "├─ 插件管理器", True)
            
            if self.collected_logs['plugins']['success']:
                self.log("INFO", f"│   └─ 加载插件 ({len(self.collected_logs['plugins']['success'])}/{len(self.collected_logs['plugins']['success']) + len(self.collected_logs['plugins']['failed'])})", True)
                
                for i, plugin in enumerate(self.collected_logs['plugins']['success']):
                    prefix = "│       ├─ " if i < len(self.collected_logs['plugins']['success']) - 1 else "│       └─ "
                    self.log("INFO", f"{prefix}{plugin}", True)
                
                for i, plugin in enumerate(self.collected_logs['plugins']['failed']):
                    prefix = "│       ├─ " if i < len(self.collected_logs['plugins']['failed']) - 1 else "│       └─ "
                    self.log("ERROR", f"{prefix}{plugin}", False)
        
        if self.collected_logs['services']['success'] or self.collected_logs['services']['failed']:
            self.log("INFO", "├─ 服务发现", True)
            
            if self.collected_logs['services']['success']:
                self.log("INFO", f"│   └─ 业务服务 ({len(self.collected_logs['services']['success'])}/{len(self.collected_logs['services']['success']) + len(self.collected_logs['services']['failed'])})", True)
                
                for i, service in enumerate(self.collected_logs['services']['success']):
                    prefix = "│       ├─ " if i < len(self.collected_logs['services']['success']) - 1 else "│       └─ "
                    self.log("INFO", f"{prefix}{service}", True)
                
                for i, service in enumerate(self.collected_logs['services']['failed']):
                    prefix = "│       ├─ " if i < len(self.collected_logs['services']['failed']) - 1 else "│       └─ "
                    self.log("ERROR", f"{prefix}{service}", False)
        
        if self.collected_logs['apis']['success'] or self.collected_logs['apis']['failed']:
            self.log("INFO", "└─ API映射", True)
            
            if self.collected_logs['apis']['success']:
                self.log("INFO", f"│   └─ ({len(self.collected_logs['apis']['success'])})", True)
        
        if self.collected_logs['warnings']:
            self.log("INFO", "└─ 警告汇总 ({len(self.collected_logs['warnings'])})", None)
            
            for warning in self.collected_logs['warnings']:
                self.log("WARNING", warning, None)
        
        if self.collected_logs['errors']:
            self.log("INFO", "└─ 错误汇总 ({len(self.collected_logs['errors'])})", None)
            
            for error in self.collected_logs['errors']:
                self.log("ERROR", error, False)
    
    def set_level(self, level: str) -> None:
        """
        设置日志级别
        
        Args:
            level: 日志级别（英文）
        """
        level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        self.logger.setLevel(level_map[level])
    
    def get_logger(self) -> logging.Logger:
        """
        获取底层的logging.Logger对象
        
        Returns:
            logging.Logger: logging.Logger对象
        """
        return self.logger


class UvicornLogHandler(logging.Handler):
    """
    Uvicorn 日志处理器，拦截并格式化 uvicorn 的日志输出
    """
    
    def __init__(self, target_logger):
        """
        初始化 Uvicorn 日志处理器
        
        Args:
            target_logger: 目标 Logger 实例，用于输出格式化后的日志
        """
        super().__init__()
        self.target_logger = target_logger
    
    def emit(self, record: logging.LogRecord):
        """
        发送日志记录到目标 Logger
        
        Args:
            record: 日志记录对象
        """
        try:
            message = record.getMessage()
            levelname = record.levelname
            
            # 映射到我们的日志方法
            if levelname == "DEBUG":
                self.target_logger.debug(f"[uvicorn] {message}")
            elif levelname == "INFO":
                self.target_logger.info(f"[uvicorn] {message}")
            elif levelname == "WARNING":
                self.target_logger.warning(f"[uvicorn] {message}")
            elif levelname == "ERROR":
                self.target_logger.error(f"[uvicorn] {message}")
            elif levelname == "CRITICAL":
                self.target_logger.critical(f"[uvicorn] {message}")
        except Exception:
            self.handleError(record)

# 全局日志管理器
class LogManager:
    """
    日志管理器，用于管理多个日志实例
    """
    
    def __init__(self):
        self.loggers: Dict[str, Logger] = {}
        self.default_log_file: Optional[str] = None
        self.default_log_type: str = "linkgateway"
    
    def get_logger(self, name: str, log_file: Optional[str] = None, log_type: str = "linkgateway") -> Logger:
        """
        获取或创建日志实例
        
        Args:
            name: 日志名称
            log_file: 日志文件路径
            log_type: 日志类型，linkgateway或engine
            
        Returns:
            Logger: 日志实例
        """
        # 使用name作为主要key，确保每个名称只对应一个实例
        if name not in self.loggers:
            # 如果没有提供log_file，使用默认值
            effective_log_file = log_file or self.default_log_file
            # 创建并存储日志实例
            self.loggers[name] = Logger(name, effective_log_file, log_type)
        return self.loggers[name]
    
    def set_level(self, level: str) -> None:
        """
        设置所有日志实例的日志级别
        
        Args:
            level: 日志级别（英文）
        """
        for logger in self.loggers.values():
            logger.set_level(level)
    
    def set_default_log_file(self, log_file: str) -> None:
        """
        设置默认日志文件路径
        
        Args:
            log_file: 默认日志文件路径
        """
        self.default_log_file = log_file
    
    def clear(self) -> None:
        """
        清理所有日志实例
        """
        # 清理已初始化的logger标记
        Logger.initialized_loggers.clear()
        # 清理日志实例
        self.loggers.clear()

# 创建全局日志管理器实例
global_log_manager = LogManager()

# 便捷函数
def get_logger(name: str, log_file: Optional[str] = None, log_type: str = "linkgateway") -> Logger:
    """
    获取或创建日志实例
    
    Args:
        name: 日志名称
        log_file: 日志文件路径
        log_type: 日志类型，linkgateway或engine
        
    Returns:
        Logger: 日志实例
    """
    return global_log_manager.get_logger(name, log_file, log_type)

# 创建默认的LinkGateway日志实例
logger = get_logger("LinkGateway")
