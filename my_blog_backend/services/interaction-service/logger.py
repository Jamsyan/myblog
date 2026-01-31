import os
import sys
import logging
import csv
from logging.handlers import TimedRotatingFileHandler
from typing import Optional
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
        if not os.path.exists(self.filename):
            log_dir = os.path.dirname(self.filename)
            if log_dir and not os.path.exists(log_dir):
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


def get_logger(name: str = "interaction-service", log_dir: Optional[str] = None) -> logging.Logger:
    """
    获取或创建日志实例
    控制台输出结构化格式，文件和CSV输出保留完整信息
    
    Args:
        name: 日志名称
        log_dir: 日志目录路径，默认使用项目根目录下的log/services目录
        
    Returns:
        logging.Logger: 配置好的日志记录器实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(StructuredFormatter())
    logger.addHandler(console_handler)
    
    if not log_dir:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        log_dir = os.path.join(project_root, "log", "services", "interaction-service")
    
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, "interaction-service")
    
    debug_info_handler = TimedRotatingFileHandler(
        filename=f"{log_file}.debug_info",
        when="H",
        interval=1,
        backupCount=24,
        encoding="utf-8"
    )
    debug_info_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s:] %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    debug_info_handler.setFormatter(file_formatter)
    debug_info_handler.addFilter(lambda record: record.levelno in (logging.DEBUG, logging.INFO))
    logger.addHandler(debug_info_handler)
    
    warning_handler = TimedRotatingFileHandler(
        filename=f"{log_file}.warning",
        when="D",
        interval=1,
        backupCount=3,
        encoding="utf-8"
    )
    warning_handler.setLevel(logging.WARNING)
    warning_handler.setFormatter(file_formatter)
    warning_handler.addFilter(lambda record: record.levelno == logging.WARNING)
    logger.addHandler(warning_handler)
    
    error_critical_handler = TimedRotatingFileHandler(
        filename=f"{log_file}.error",
        when="D",
        interval=1,
        backupCount=14,
        encoding="utf-8"
    )
    error_critical_handler.setLevel(logging.ERROR)
    error_critical_handler.setFormatter(file_formatter)
    error_critical_handler.addFilter(lambda record: record.levelno in (logging.ERROR, logging.CRITICAL))
    logger.addHandler(error_critical_handler)
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    csv_log_file = os.path.join(project_root, "log", "logs.csv")
    csv_handler = CSVLogHandler(
        filename=csv_log_file,
        encoding="utf-8"
    )
    csv_handler.setLevel(logging.DEBUG)
    logger.addHandler(csv_handler)
    
    return logger


logger = get_logger()
