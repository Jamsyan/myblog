import os
import json
from typing import Dict, Any, Optional, Callable, List
from fastapi import APIRouter, Request, Response, HTTPException
from .logs import get_logger

class ServiceProxy:
    """
    服务代理类，负责处理服务到引擎的请求转发
    确保引擎API不直接对外暴露，所有请求通过代理层处理
    """
    
    def __init__(self, registry):
        """
        初始化服务代理
        
        Args:
            registry: 服务注册表，用于获取引擎实例
        """
        # 检查registry参数
        if not registry:
            raise ValueError("Registry cannot be None")
        
        self.registry = registry
        self.logger = get_logger("ServiceProxy")
        self.router = APIRouter(prefix="/internal/proxy")
        self._setup_routes()
        self.logger.info("ServiceProxy initialized successfully")
    
    def _setup_routes(self):
        """
        设置代理路由
        支持所有HTTP方法，确保引擎API只能通过内部代理访问
        """
        @self.router.api_route("/{engine_id}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def proxy_request(engine_id: str, request: Request):
            """
            代理请求到引擎
            
            Args:
                engine_id: 引擎ID
                request: FastAPI请求对象
                
            Returns:
                Any: 请求处理结果
            """
            try:
                body = await self._parse_request_body(request)
                action, data = self._extract_action_and_data(request, body)
                
                self._validate_action(action)
                self._validate_engine_health(engine_id)
                
                result = self._call_engine(engine_id, action, data)
                return result
            except HTTPException:
                raise
            except Exception as e:
                return self._handle_proxy_error(e, engine_id)
    
    async def _parse_request_body(self, request: Request) -> Dict[str, Any]:
        """
        解析请求体
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            Dict[str, Any]: 解析后的请求体
        """
        try:
            return await request.json()
        except Exception as e:
            self.logger.debug(f"非JSON请求体: {str(e)}")
            try:
                raw_body = await request.body()
                if raw_body:
                    return {"raw_body": raw_body.decode('utf-8', errors='ignore')}
            except:
                pass
            return {}
    
    def _extract_action_and_data(self, request: Request, body: Dict[str, Any]) -> tuple:
        """
        从请求中提取action和data
        
        Args:
            request: FastAPI请求对象
            body: 请求体
            
        Returns:
            tuple: (action, data)
        """
        if request.method == "GET":
            action = request.query_params.get("action")
            data = dict(request.query_params)
            if "action" in data:
                del data["action"]
            data["request_method"] = request.method
            return action, data
        
        if isinstance(body, dict):
            action = body.get("action")
            data = body.get("data", {})
            if not action:
                action = body.get("action")
                if action:
                    data = {k: v for k, v in body.items() if k != "action"}
            data["request_method"] = request.method
            return action, data
        
        return None, {}
    
    def _validate_action(self, action: str) -> None:
        """
        验证action字段
        
        Args:
            action: 请求动作
            
        Raises:
            HTTPException: action为空时抛出
        """
        if not action:
            self.logger.error(f"请求缺少action字段")
            raise HTTPException(status_code=400, detail={"error": "Missing 'action' field"})
    
    def _validate_engine_health(self, engine_id: str) -> None:
        """
        验证引擎健康状态
        
        Args:
            engine_id: 引擎ID
            
        Raises:
            HTTPException: 引擎不健康或不存在时抛出
        """
        engine = self.registry.get_engine(engine_id)
        if not engine:
            self.logger.error(f"引擎未找到: {engine_id}")
            raise HTTPException(status_code=404, detail={"error": f"Engine {engine_id} not found"})
        
        if not self.registry.check_service_health(engine_id):
            self.logger.error(f"引擎不健康: {engine_id}")
            raise HTTPException(status_code=503, detail={"error": f"Engine {engine_id} is not healthy"})
    
    def _call_engine(self, engine_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用引擎的handle_request方法
        
        Args:
            engine_id: 引擎ID
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 处理结果
        """
        engine = self.registry.get_engine(engine_id)
        self.logger.info(f"转发请求到引擎: {engine_id}, 动作: {action}")
        
        try:
            result = engine.handle_request(action, data)
            if not isinstance(result, dict):
                result = {"result": result}
            if "status" not in result:
                result["status"] = "success"
        except Exception as e:
            self.logger.error(f"引擎处理请求失败: {str(e)}")
            result = {
                "status": "error",
                "error": str(e),
                "action": action,
                "engine_id": engine_id
            }
        
        self.logger.info(f"引擎返回结果: {engine_id}, 动作: {action}, 状态: {result.get('status')}")
        return result
    
    def _handle_proxy_error(self, error: Exception, engine_id: str) -> HTTPException:
        """
        处理代理错误
        
        Args:
            error: 异常对象
            engine_id: 引擎ID
            
        Returns:
            HTTPException: HTTP异常
        """
        self.logger.error(f"代理请求失败: {str(error)}")
        error_response = {
            "status": "error",
            "error": f"Proxy request failed: {str(error)}",
            "engine_id": engine_id
        }
        return HTTPException(status_code=500, detail=error_response)
    
    def get_router(self) -> APIRouter:
        """
        获取代理路由器
        
        Returns:
            APIRouter: 代理路由器
        """
        return self.router
    
    async def forward_request(self, engine_id: str, action: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        转发请求到引擎
        
        Args:
            engine_id: 引擎ID
            action: 请求动作
            data: 请求数据
            
        Returns:
            Dict[str, Any]: 请求处理结果
        """
        try:
            # 验证参数
            if not engine_id:
                self.logger.error("Engine ID cannot be empty")
                return {"status": "error", "error": "Engine ID cannot be empty"}
            
            if not action:
                self.logger.error("Action cannot be empty")
                return {"status": "error", "error": "Action cannot be empty"}
            
            # 确保data是字典格式
            if not isinstance(data, dict):
                data = {"data": data}
            
            # 获取引擎实例
            engine = self.registry.get_engine(engine_id)
            if not engine:
                self.logger.error(f"引擎未找到: {engine_id}")
                return {"status": "error", "error": f"Engine {engine_id} not found", "engine_id": engine_id}
            
            # 验证引擎是否健康
            if not self.registry.check_service_health(engine_id):
                self.logger.error(f"引擎不健康: {engine_id}")
                return {"status": "error", "error": f"Engine {engine_id} is not healthy", "engine_id": engine_id}
            
            self.logger.info(f"转发请求到引擎: {engine_id}, 动作: {action}")
            
            # 调用引擎的handle_request方法
            try:
                result = engine.handle_request(action, data)
                # 确保返回结果是字典格式
                if not isinstance(result, dict):
                    result = {"result": result}
                # 添加状态字段
                if "status" not in result:
                    result["status"] = "success"
                # 添加引擎信息
                result["engine_id"] = engine_id
                result["action"] = action
            except Exception as e:
                self.logger.error(f"引擎处理请求失败: {str(e)}")
                # 构建统一的错误响应
                result = {
                    "status": "error",
                    "error": str(e),
                    "action": action,
                    "engine_id": engine_id
                }
            
            self.logger.info(f"引擎返回结果: {engine_id}, 动作: {action}, 状态: {result.get('status')}")
            
            return result
        except Exception as e:
            self.logger.error(f"转发请求失败: {str(e)}")
            # 构建统一的错误响应
            return {
                "status": "error",
                "error": f"Forward request failed: {str(e)}",
                "engine_id": engine_id,
                "action": action
            }
    
    def get_available_engines(self) -> List[Dict[str, Any]]:
        """
        获取可用的引擎列表
        
        Returns:
            List[Dict[str, Any]]: 引擎列表
        """
        try:
            engines = self.registry.list_services(service_type="engine")
            if not isinstance(engines, list):
                self.logger.error("Registry returned invalid engines list")
                return []
            
            healthy_engines = []
            for engine in engines:
                engine_info = self._extract_healthy_engine_info(engine)
                if engine_info:
                    healthy_engines.append(engine_info)
            
            self.logger.info(f"Found {len(healthy_engines)} healthy engines")
            return healthy_engines
        except Exception as e:
            self.logger.error(f"Failed to get available engines: {str(e)}")
            return []
    
    def _extract_healthy_engine_info(self, engine: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        提取健康的引擎信息
        
        Args:
            engine: 引擎信息
            
        Returns:
            Optional[Dict[str, Any]]: 健康的引擎信息，不健康返回None
        """
        if not isinstance(engine, dict):
            return None
        
        if "info" not in engine:
            return None
        
        info = engine["info"]
        if not isinstance(info, dict):
            return None
        
        engine_id = info.get("service_id")
        if not engine_id:
            return None
        
        if not self.registry.check_service_health(engine_id):
            return None
        
        return info
    
    def get_engine_info(self, engine_id: str) -> Optional[Dict[str, Any]]:
        """
        获取引擎信息
        
        Args:
            engine_id: 引擎ID
            
        Returns:
            Optional[Dict[str, Any]]: 引擎信息
        """
        try:
            if not engine_id:
                self.logger.error("Engine ID cannot be empty")
                return None
            
            service = self.registry.get_service(engine_id)
            if isinstance(service, dict) and service.get("type") == "engine" and "info" in service:
                info = service["info"]
                if isinstance(info, dict):
                    # 添加健康状态信息
                    info["healthy"] = self.registry.check_service_health(engine_id)
                    return info
            
            self.logger.warning(f"Engine not found or not an engine: {engine_id}")
            return None
        except Exception as e:
            self.logger.error(f"Failed to get engine info: {str(e)}")
            return None