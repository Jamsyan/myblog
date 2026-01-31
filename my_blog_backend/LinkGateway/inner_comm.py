from typing import Dict, Any, Optional, List
from .protocol import Request, Response

class InnerCommunicator:
    """
    内环通信类，负责内核引擎之间的通信
    """
    
    def __init__(self):
        """
        初始化内环通信器
        """
        self.engine_registry: Dict[str, Any] = {}
        self.message_queue: List[Dict[str, Any]] = []
    
    def register_engine(self, engine_id: str, engine: Any) -> bool:
        """
        注册引擎到内环通信器
        
        Args:
            engine_id: 引擎ID
            engine: 引擎实例
            
        Returns:
            bool: 注册成功返回True，失败返回False
        """
        self.engine_registry[engine_id] = engine
        return True
    
    def unregister_engine(self, engine_id: str) -> bool:
        """
        从内环通信器中注销引擎
        
        Args:
            engine_id: 引擎ID
            
        Returns:
            bool: 注销成功返回True，失败返回False
        """
        if engine_id in self.engine_registry:
            del self.engine_registry[engine_id]
            return True
        return False
    
    def send_request(self, target_engine_id: str, action: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        发送请求到目标引擎
        
        Args:
            target_engine_id: 目标引擎ID
            action: 请求动作
            data: 请求数据
            
        Returns:
            Optional[Dict[str, Any]]: 请求结果，未找到目标引擎返回None
        """
        # 检查目标引擎是否存在
        if target_engine_id not in self.engine_registry:
            return None
        
        # 获取目标引擎
        engine = self.engine_registry[target_engine_id]
        
        # 构建请求
        request = Request(
            service_id=target_engine_id,
            action=action,
            data=data or {}
        )
        
        # 发送请求并获取响应
        try:
            # 调用引擎的handle_request方法
            response_data = engine.handle_request(action, data or {})
            
            # 构建响应
            response = Response.success(
                request_id=request.request_id,
                data=response_data
            )
            
            return response.dict()
        except Exception as e:
            # 构建错误响应
            response = Response.error(
                request_id=request.request_id,
                code=500,
                error=str(e)
            )
            
            return response.dict()
    
    def send_async_request(self, target_engine_id: str, action: str, data: Dict[str, Any] = None) -> str:
        """
        发送异步请求到目标引擎
        
        Args:
            target_engine_id: 目标引擎ID
            action: 请求动作
            data: 请求数据
            
        Returns:
            str: 请求ID
        """
        # 构建请求
        request = Request(
            service_id=target_engine_id,
            action=action,
            data=data or {}
        )
        
        # 将请求加入消息队列
        self.message_queue.append({
            "request": request,
            "status": "pending"
        })
        
        return request.request_id
    
    def process_message_queue(self) -> List[Dict[str, Any]]:
        """
        处理消息队列中的请求
        
        Returns:
            List[Dict[str, Any]]: 处理结果列表
        """
        results = []
        
        for message in self.message_queue:
            request = message["request"]
            target_engine_id = request.service_id
            
            result = self._process_single_message(request, target_engine_id)
            results.append(result)
        
        self.message_queue.clear()
        return results
    
    def _process_single_message(self, request: Any, target_engine_id: str) -> Dict[str, Any]:
        """
        处理单个消息
        
        Args:
            request: 请求对象
            target_engine_id: 目标引擎ID
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        # 检查目标引擎是否存在
        if target_engine_id not in self.engine_registry:
            response = Response.error(
                request_id=request.request_id,
                code=404,
                error=f"Engine {target_engine_id} not found"
            )
            return {
                "request_id": request.request_id,
                "status": "error",
                "response": response.dict()
            }
        
        engine = self.engine_registry[target_engine_id]
        
        try:
            response_data = engine.handle_request(request.action, request.data)
            response = Response.success(
                request_id=request.request_id,
                data=response_data
            )
            return {
                "request_id": request.request_id,
                "status": "success",
                "response": response.dict()
            }
        except Exception as e:
            response = Response.error(
                request_id=request.request_id,
                code=500,
                error=str(e)
            )
            return {
                "request_id": request.request_id,
                "status": "error",
                "response": response.dict()
            }
    
    def broadcast(self, action: str, data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        广播消息到所有注册的引擎
        
        Args:
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 广播结果，包含每个引擎的响应
        """
        results = {}
        
        # 向每个注册的引擎发送请求
        for engine_id, engine in self.engine_registry.items():
            try:
                # 调用引擎的handle_request方法
                response_data = engine.handle_request(action, data or {})
                
                results[engine_id] = {
                    "status": "success",
                    "data": response_data
                }
            except Exception as e:
                results[engine_id] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return results
    
    def get_engine(self, engine_id: str) -> Optional[Any]:
        """
        获取引擎实例
        
        Args:
            engine_id: 引擎ID
            
        Returns:
            Optional[Any]: 引擎实例，未找到返回None
        """
        return self.engine_registry.get(engine_id)
    
    def list_engines(self) -> List[str]:
        """
        列出所有注册的引擎ID
        
        Returns:
            List[str]: 引擎ID列表
        """
        return list(self.engine_registry.keys())
