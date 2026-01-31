from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from LinkGateway.plugin import Plugin


class PerformanceMonitorPlugin(Plugin):
    """
    性能监控插件
    记录引擎调用耗时、慢查询告警
    """
    
    def __init__(self, gateway):
        super().__init__(gateway)
        
        # 性能统计
        self.engine_call_stats = {}  # {engine_id: {action: [durations]}}
        
        # 慢查询阈值（秒）
        self.slow_query_threshold = 1.0
        
        # 告警配置
        self.alert_enabled = True
        self.alert_cooldown = 300  # 告警冷却时间（秒）
        self.last_alert_time = {}  # {engine_id: action: last_alert_time}
        
        self.logger.info("性能监控插件初始化完成")
    
    def initialize(self) -> bool:
        """
        初始化插件
        """
        try:
            self.logger.info("初始化性能监控插件")
            return super().initialize()
        except Exception as e:
            self.logger.error(f"初始化性能监控插件失败: {str(e)}")
            return False
    
    def on_service_calling_engine(self, service_id: str, engine_id: str, action: str, data: Dict[str, Any]) -> None:
        """
        服务调用引擎时的钩子
        记录调用开始时间
        """
        if engine_id not in self.engine_call_stats:
            self.engine_call_stats[engine_id] = {}
        
        # 记录调用开始时间
        self.engine_call_stats[engine_id][action] = {
            "start_time": datetime.now(),
            "service_id": service_id
        }
    
    def on_engine_responding(self, engine_id: str, action: str, response: Dict[str, Any]) -> None:
        """
        引擎响应时的钩子
        计算调用耗时并检查慢查询
        """
        if engine_id not in self.engine_call_stats:
            return
        
        if action not in self.engine_call_stats[engine_id]:
            return
        
        call_info = self.engine_call_stats[engine_id][action]
        start_time = call_info["start_time"]
        
        # 计算耗时
        duration = (datetime.now() - start_time).total_seconds()
        
        # 记录耗时
        if "durations" not in call_info:
            call_info["durations"] = []
        call_info["durations"].append(duration)
        
        # 检查是否为慢查询
        is_slow = duration > self.slow_query_threshold
        
        if is_slow and self.alert_enabled:
            # 检查告警冷却
            alert_key = f"{engine_id}:{action}"
            now = datetime.now()
            
            if alert_key in self.last_alert_time:
                last_alert = self.last_alert_time[alert_key]
                if (now - last_alert).total_seconds() < self.alert_cooldown:
                    # 还在冷却期，不重复告警
                    return
            
            # 记录告警
            self.last_alert_time[alert_key] = now
            self.logger.warning(
                f"慢查询告警: 引擎 {engine_id}, 动作 {action}, "
                f"耗时 {duration:.3f}s (阈值: {self.slow_query_threshold}s)"
            )
        
        # 记录性能数据
        self.logger.debug(
            f"引擎调用完成: {engine_id}.{action}, "
            f"耗时: {duration:.3f}s, "
            f"平均耗时: {sum(call_info['durations']) / len(call_info['durations']):.3f}s, "
            f"调用次数: {len(call_info['durations'])}"
        )
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        获取性能统计信息
        
        Returns:
            Dict[str, Any]: 性能统计信息
        """
        stats = {}
        
        for engine_id, actions in self.engine_call_stats.items():
            engine_stats = {}
            
            for action, call_info in actions.items():
                durations = call_info.get("durations", [])
                
                if not durations:
                    continue
                
                avg_duration = sum(durations) / len(durations)
                max_duration = max(durations)
                min_duration = min(durations)
                call_count = len(durations)
                
                engine_stats[action] = {
                    "call_count": call_count,
                    "avg_duration": round(avg_duration, 3),
                    "max_duration": round(max_duration, 3),
                    "min_duration": round(min_duration, 3),
                    "slow_queries": sum(1 for d in durations if d > self.slow_query_threshold)
                }
            
            stats[engine_id] = engine_stats
        
        return {
            "statistics": stats,
            "config": {
                "slow_query_threshold": self.slow_query_threshold,
                "alert_cooldown": self.alert_cooldown,
                "alert_enabled": self.alert_enabled
            }
        }
    
    def reset_stats(self) -> None:
        """
        重置性能统计
        """
        self.engine_call_stats.clear()
        self.last_alert_time.clear()
        self.logger.info("性能统计已重置")
    
    def set_slow_query_threshold(self, threshold: float) -> None:
        """
        设置慢查询阈值
        
        Args:
            threshold: 阈值（秒）
        """
        self.slow_query_threshold = threshold
        self.logger.info(f"慢查询阈值已设置为 {threshold}s")