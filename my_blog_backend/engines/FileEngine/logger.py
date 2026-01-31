import os
import sys
import logging
import csv
from logging.handlers import RotatingFileHandler
from datetime import datetime

try:
    from colorama import init
    init()
except ImportError:
    pass


class LogColor:
    RESET = "\033[0m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    
    LEVEL_COLORS = {
        "DEBUG": GREEN,
        "INFO": CYAN,
        "WARNING": YELLOW,
        "ERROR": RED,
        "CRITICAL": MAGENTA
    }


class StructuredFormatter(logging.Formatter):
    """
    结构化日志格式化器，实现固定宽度的列对齐格式
    格式：[等级] [组件名] - 操作描述 [状态]
    """
    
    def __init__(self):
        super().__init__()
        self.level_width = 8
        self.name_width = 18
        self.desc_width = 40
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


class CSVLogHandler(logging.Handler):
    """
    CSV 格式的日志处理器，将日志以表格形式存储
    统一存储到 log/logs.csv，保留完整日志消息
    """
    
    def __init__(self, filename: str, encoding: str = "utf-8"):
        super().__init__()
        self.filename = filename
        self.encoding = encoding
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        if os.path.exists(self.filename):
            return
        
        log_dir = os.path.dirname(self.filename)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        with open(self.filename, 'w', encoding=self.encoding, newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['时间戳', '日志级别', '服务ID', '请求ID', '模块名', '消息'])
    
    def emit(self, record: logging.LogRecord):
        try:
            timestamp = datetime.datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S')
            levelname = record.levelname
            service_id = getattr(record, 'service_id', 'unknown')
            request_id = getattr(record, 'request_id', 'unknown')
            name = record.name
            message = record.getMessage()
            
            with open(self.filename, 'a', encoding=self.encoding, newline='') as f:
                writer = csv.writer(f)
                writer.writerow([timestamp, levelname, service_id, request_id, name, message])
        except Exception:
            self.handleError(record)


def setup_logger(engine_name: str, project_root: str) -> logging.Logger:
    """
    设置日志记录器
    控制台输出结构化格式，文件和CSV输出保留完整信息
    
    Args:
        engine_name: 引擎名称
        project_root: 项目根目录路径
        
    Returns:
        logging.Logger: 配置好的日志记录器
    """
    logger = logging.getLogger(engine_name)
    logger.setLevel(logging.DEBUG)
    
    if logger.handlers:
        return logger
    
    log_dir = os.path.join(project_root, "log", "engines", engine_name)
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, engine_name)
    
    _add_console_handler(logger)
    _add_file_handlers(logger, log_file)
    _add_csv_handler(logger, project_root)
    
    return logger


def _add_console_handler(logger: logging.Logger):
    """
    添加控制台处理器
    
    Args:
        logger: 日志记录器
    """
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)


def _add_file_handlers(logger: logging.Logger, log_file: str):
    """
    添加文件处理器
    
    Args:
        logger: 日志记录器
        log_file: 日志文件路径
    """
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s:] %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    info_handler = RotatingFileHandler(
        f"{log_file}.info",
        maxBytes=10*1024*1024,
        backupCount=24,
        encoding='utf-8'
    )
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(file_formatter)
    logger.addHandler(info_handler)
    
    error_handler = RotatingFileHandler(
        f"{log_file}.error",
        maxBytes=10*1024*1024,
        backupCount=14,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.WARNING)
    error_handler.setFormatter(file_formatter)
    logger.addHandler(error_handler)


def _add_csv_handler(logger: logging.Logger, project_root: str):
    """
    添加CSV处理器
    
    Args:
        logger: 日志记录器
        project_root: 项目根目录路径
    """
    csv_log_file = os.path.join(project_root, "log", "logs.csv")
    csv_handler = CSVLogHandler(
        filename=csv_log_file,
        encoding="utf-8"
    )
    csv_handler.setLevel(logging.DEBUG)
    logger.addHandler(csv_handler)


class Logger:
    """
    日志管理类，封装了日志记录的常用方法
    """
    
    def __init__(self, engine_name: str, project_root: str):
        """
        初始化日志管理类
        
        Args:
            engine_name: 引擎名称
            project_root: 项目根目录路径
        """
        self.logger = setup_logger(engine_name, project_root)
    
    def debug(self, message: str):
        """
        记录DEBUG级别的日志
        
        Args:
            message: 日志消息
        """
        self.logger.debug(message)
    
    def info(self, message: str):
        """
        记录INFO级别的日志
        
        Args:
            message: 日志消息
        """
        self.logger.info(message)
    
    def warning(self, message: str):
        """
        记录WARNING级别的日志
        
        Args:
            message: 日志消息
        """
        self.logger.warning(message)
    
    def error(self, message: str):
        """
        记录ERROR级别的日志
        
        Args:
            message: 日志消息
        """
        self.logger.error(message)
    
    def critical(self, message: str):
        """
        记录CRITICAL级别的日志
        
        Args:
            message: 日志消息
        """
        self.logger.critical(message)
