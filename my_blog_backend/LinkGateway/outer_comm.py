import httpx
from typing import Dict, Any, Optional, List
from .protocol import Request, Response

class OuterCommunicator:
    """
    外环通信类，负责与网络引擎及外部系统的通信
    """
    
    def __init__(self):
        """
        初始化外环通信器
        """
        self.client = httpx.AsyncClient(timeout=30)
        self.network_engines: Dict[str, Dict[str, Any]] = {}
    
    def register_network_engine(self, engine_id: str, engine_info: Dict[str, Any]) -> bool:
        """
        注册网络引擎
        
        Args:
            engine_id: 引擎ID
            engine_info: 引擎信息，包含引擎的网络地址等
            
        Returns:
            bool: 注册成功返回True，失败返回False
        """
        self.network_engines[engine_id] = engine_info
        return True
    
    def unregister_network_engine(self, engine_id: str) -> bool:
        """
        注销网络引擎
        
        Args:
            engine_id: 引擎ID
            
        Returns:
            bool: 注销成功返回True，失败返回False
        """
        if engine_id in self.network_engines:
            del self.network_engines[engine_id]
            return True
        return False
    
    async def send_request(self, target_engine_id: str, action: str, data: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        发送请求到网络引擎
        
        Args:
            target_engine_id: 目标引擎ID
            action: 请求动作
            data: 请求数据
            
        Returns:
            Optional[Dict[str, Any]]: 请求结果，未找到目标引擎返回None
        """
        # 检查目标引擎是否存在
        if target_engine_id not in self.network_engines:
            return None
        
        # 获取目标引擎信息
        engine_info = self.network_engines[target_engine_id]
        base_url = engine_info.get("base_url")
        
        if not base_url:
            return None
        
        # 构建请求URL
        url = f"{base_url}/api/{action}"
        
        # 构建请求数据
        request = Request(
            service_id=target_engine_id,
            action=action,
            data=data or {}
        )
        
        # 发送HTTP请求
        try:
            response = await self.client.post(
                url,
                json=request.dict(),
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            # 检查响应状态码
            if response.status_code == 200:
                return response.json()
            else:
                # 构建错误响应
                return Response.error(
                    request_id=request.request_id,
                    code=response.status_code,
                    error=f"HTTP error {response.status_code}: {response.text}"
                ).dict()
        except httpx.RequestError as e:
            # 构建错误响应
            return Response.error(
                request_id=request.request_id,
                code=500,
                error=f"Request error: {str(e)}"
            ).dict()
    
    async def send_webhook(self, url: str, data: Dict[str, Any] = None) -> bool:
        """
        发送Webhook请求
        
        Args:
            url: Webhook URL
            data: 请求数据
            
        Returns:
            bool: 请求成功返回True，失败返回False
        """
        try:
            response = await self.client.post(
                url,
                json=data or {},
                headers={
                    "Content-Type": "application/json"
                }
            )
            
            return response.status_code == 200
        except httpx.RequestError:
            return False
    
    async def fetch_data(self, url: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        从外部API获取数据
        
        Args:
            url: API URL
            params: 查询参数
            
        Returns:
            Optional[Dict[str, Any]]: 获取的数据，请求失败返回None
        """
        try:
            response = await self.client.get(
                url,
                params=params or {}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
        except httpx.RequestError:
            return None
    
    def get_network_engine(self, engine_id: str) -> Optional[Dict[str, Any]]:
        """
        获取网络引擎信息
        
        Args:
            engine_id: 引擎ID
            
        Returns:
            Optional[Dict[str, Any]]: 引擎信息，未找到返回None
        """
        return self.network_engines.get(engine_id)
    
    def list_network_engines(self) -> List[str]:
        """
        列出所有注册的网络引擎ID
        
        Returns:
            List[str]: 网络引擎ID列表
        """
        return list(self.network_engines.keys())
    
    async def close(self) -> None:
        """
        关闭HTTP客户端
        """
        await self.client.aclose()
