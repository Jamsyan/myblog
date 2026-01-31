import threading
import queue
import time
from typing import Callable, Any


class QueueManager:
    """
    队列管理器，用于处理高并发情况下的任务，避免文件读写冲突
    """
    
    def __init__(self, max_workers: int = 5, logger=None):
        """
        初始化队列管理器
        
        Args:
            max_workers: 最大工作线程数
            logger: 日志记录器实例
        """
        self.task_queue = queue.Queue()
        self.max_workers = max_workers
        self.workers = []
        self.running = False
        self.logger = logger
        
    def start(self):
        """
        启动队列管理器
        """
        if self.running:
            return
        
        self.running = True
        
        # 创建工作线程
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, name=f"queue-worker-{i}")
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        """
        停止队列管理器
        """
        self.running = False
        
        # 等待所有工作线程完成
        for worker in self.workers:
            worker.join(timeout=1.0)
        
        self.workers.clear()
    
    def _worker_loop(self):
        """
        工作线程循环，处理队列中的任务
        """
        while self.running:
            task = self._get_task_from_queue()
            if task is None:
                continue
            
            self._execute_task(task)
    
    def _get_task_from_queue(self):
        """
        从队列获取任务
        
        Returns:
            Optional[Callable]: 任务函数，队列为空返回None
        """
        try:
            return self.task_queue.get(timeout=1.0)
        except queue.Empty:
            return None
    
    def _execute_task(self, task: Callable[[], Any]):
        """
        执行任务
        
        Args:
            task: 任务函数
        """
        try:
            task()
        except Exception as e:
            self._log_error(f"执行任务出错: {str(e)}")
        finally:
            self.task_queue.task_done()
    
    def _log_error(self, message: str):
        """
        记录错误日志
        
        Args:
            message: 错误消息
        """
        if self.logger:
            self.logger.error(message)
        else:
            print(message)
    
    def add_task(self, task: Callable[[], Any]) -> bool:
        """
        添加任务到队列
        
        Args:
            task: 要执行的任务函数
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        if not self.running:
            return self._execute_task_directly(task)
        
        return self._add_task_to_queue(task)
    
    def _execute_task_directly(self, task: Callable[[], Any]) -> bool:
        """
        直接执行任务（队列未运行时）
        
        Args:
            task: 任务函数
            
        Returns:
            bool: 执行成功返回True，失败返回False
        """
        try:
            task()
            return True
        except Exception as e:
            self._log_error(f"直接执行任务出错: {str(e)}")
            return False
    
    def _add_task_to_queue(self, task: Callable[[], Any]) -> bool:
        """
        添加任务到队列
        
        Args:
            task: 任务函数
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        try:
            self.task_queue.put(task)
            return True
        except Exception as e:
            self._log_error(f"添加任务到队列出错: {str(e)}")
            return False
    
    def wait_for_completion(self, timeout: float = None):
        """
        等待队列中所有任务完成
        
        Args:
            timeout: 超时时间（秒）
        """
        self.task_queue.join(timeout=timeout)
    
    def get_queue_size(self) -> int:
        """
        获取队列中的任务数量
        
        Returns:
            int: 队列中的任务数量
        """
        return self.task_queue.qsize()