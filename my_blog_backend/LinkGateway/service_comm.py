from typing import Dict, Any, Optional
from .inner_comm import InnerCommunicator
from .logs import get_logger


class ServiceCommunicator:
    """
    服务层内部通信接口
    提供服务层访问 InnerCommunicator 的统一接口
    """
    
    def __init__(self, inner_comm: InnerCommunicator, logger=None):
        """
        初始化服务层通信器
        
        Args:
            inner_comm: 内部通信器实例
            logger: 日志记录器（可选）
        """
        self.inner_comm = inner_comm
        self.logger = logger or get_logger("ServiceCommunicator")
    
    def call_engine(self, engine_id: str, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        调用引擎（同步）
        
        Args:
            engine_id: 引擎ID
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 引擎返回结果
        """
        try:
            self.logger.info(f"服务层调用引擎: {engine_id}, 动作: {action}")
            
            # 使用 InnerCommunicator 发送请求
            result = self.inner_comm.send_request(engine_id, action, data or {})
            
            if result is None:
                self.logger.error(f"引擎 {engine_id} 不存在或未注册")
                return {
                    "status": "error",
                    "error": f"Engine {engine_id} not found or not registered"
                }
            
            self.logger.info(f"引擎 {engine_id} 返回结果: {result.get('status', 'unknown')}")
            return result
            
        except Exception as e:
            self.logger.error(f"调用引擎 {engine_id} 失败: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to call engine {engine_id}: {str(e)}"
            }
    
    async def call_engine_async(self, engine_id: str, action: str, data: Dict[str, Any] = None) -> str:
        """
        调用引擎（异步）
        
        Args:
            engine_id: 引擎ID
            action: 请求动作
            data: 请求数据
            
        Returns:
            str: 请求ID，可用于后续查询结果
        """
        try:
            self.logger.info(f"服务层异步调用引擎: {engine_id}, 动作: {action}")
            
            # 使用 InnerCommunicator 发送异步请求
            request_id = self.inner_comm.send_async_request(engine_id, action, data or {})
            
            self.logger.info(f"异步请求已发送，请求ID: {request_id}")
            return request_id
            
        except Exception as e:
            self.logger.error(f"异步调用引擎 {engine_id} 失败: {str(e)}")
            return ""
    
    def broadcast_to_engines(self, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        广播消息到所有引擎
        
        Args:
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 每个引擎的响应结果
        """
        try:
            self.logger.info(f"广播消息到所有引擎，动作: {action}")
            
            # 使用 InnerCommunicator 广播
            results = self.inner_comm.broadcast(action, data or {})
            
            self.logger.info(f"广播完成，收到 {len(results)} 个引擎的响应")
            return results
            
        except Exception as e:
            self.logger.error(f"广播到引擎失败: {str(e)}")
            return {}
    
    def get_engine(self, engine_id: str) -> Optional[Any]:
        """
        获取引擎实例
        
        Args:
            engine_id: 引擎ID
            
        Returns:
            Optional[Any]: 引擎实例，未找到返回None
        """
        return self.inner_comm.get_engine(engine_id)
    
    def list_engines(self) -> list:
        """
        列出所有已注册的引擎ID
        
        Returns:
            list: 引擎ID列表
        """
        return self.inner_comm.list_engines()
    
    def check_engine_health(self, engine_id: str) -> bool:
        """
        检查引擎是否健康
        
        Args:
            engine_id: 引擎ID
            
        Returns:
            bool: 健康返回True，否则返回False
        """
        try:
            engine = self.inner_comm.get_engine(engine_id)
            if engine is None:
                return False
            
            # 检查引擎状态
            if hasattr(engine, 'status'):
                return engine.status == "running"
            
            return True
            
        except Exception as e:
            self.logger.error(f"检查引擎 {engine_id} 健康状态失败: {str(e)}")
            return False