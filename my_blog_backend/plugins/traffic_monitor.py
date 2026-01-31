from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from LinkGateway.plugin import Plugin


class TrafficMonitorPlugin(Plugin):
    """
    流量监控插件
    统计请求量、实现限流
    """
    
    def __init__(self, gateway):
        super().__init__(gateway)
        
        # 请求统计
        self.request_count = {}  # {path: count}
        self.request_timestamps = {}  # {path: [timestamps]}
        
        # 限流配置
        self.rate_limit = 1000  # 每个端点每分钟最多1000次请求
        self.rate_window = 60  # 时间窗口（秒）
        
        self.logger.info("流量监控插件初始化完成")
    
    def initialize(self) -> bool:
        """
        初始化插件
        """
        try:
            self.logger.info("初始化流量监控插件")
            return super().initialize()
        except Exception as e:
            self.logger.error(f"初始化流量监控插件失败: {str(e)}")
            return False
    
    def on_request_incoming(self, request: Any) -> Optional[Any]:
        """
        外部请求进入时的钩子
        实现流量统计和限流
        """
        path = request.url.path
        method = request.method if hasattr(request, 'method') else 'GET'
        
        # 更新请求统计
        if path not in self.request_count:
            self.request_count[path] = 0
            self.request_timestamps[path] = []
        
        self.request_count[path] += 1
        self.request_timestamps[path].append(datetime.now())
        
        # 清理过期的请求记录
        self._cleanup_old_requests(path)
        
        # 检查限流
        if self._is_rate_limited(path):
            self.logger.warning(f"触发限流: {path}, 当前请求数: {self.request_count[path]}")
            return {
                "status": "error",
                "error": "Rate limit exceeded",
                "message": f"Too many requests to {path}. Please try again later.",
                "retry_after": self._get_retry_after(path)
            }
        
        return None
    
    def _cleanup_old_requests(self, path: str) -> None:
        """
        清理过期的请求记录
        """
        if path not in self.request_timestamps:
            return
        
        now = datetime.now()
        cutoff_time = now - timedelta(seconds=self.rate_window)
        
        # 只保留时间窗口内的记录
        self.request_timestamps[path] = [
            ts for ts in self.request_timestamps[path]
            if ts > cutoff_time
        ]
        
        # 更新请求计数
        self.request_count[path] = len(self.request_timestamps[path])
    
    def _is_rate_limited(self, path: str) -> bool:
        """
        检查是否触发限流
        
        Args:
            path: 请求路径
            
        Returns:
            bool: 触发限流返回True
        """
        if path not in self.request_count:
            return False
        
        return self.request_count[path] >= self.rate_limit
    
    def _get_retry_after(self, path: str) -> int:
        """
        获取重试时间（秒）
        
        Args:
            path: 请求路径
            
        Returns:
            int: 重试时间（秒）
        """
        if path not in self.request_timestamps:
            return self.rate_window
        
        # 找到最早的请求时间
        oldest_timestamp = min(self.request_timestamps[path])
        retry_after = int((oldest_timestamp + timedelta(seconds=self.rate_window) - datetime.now()).total_seconds())
        
        return max(0, retry_after)
    
    def get_traffic_stats(self) -> Dict[str, Any]:
        """
        获取流量统计信息
        
        Returns:
            Dict[str, Any]: 流量统计信息
        """
        stats = {}
        
        for path, count in self.request_count.items():
            if path not in self.request_timestamps:
                continue
            
            timestamps = self.request_timestamps[path]
            if not timestamps:
                continue
            
            # 计算最近1分钟的请求量
            now = datetime.now()
            one_minute_ago = now - timedelta(seconds=60)
            recent_count = sum(1 for ts in timestamps if ts > one_minute_ago)
            
            stats[path] = {
                "total_requests": count,
                "recent_requests": recent_count,
                "is_rate_limited": self._is_rate_limited(path)
            }
        
        return {
            "statistics": stats,
            "config": {
                "rate_limit": self.rate_limit,
                "rate_window": self.rate_window
            }
        }