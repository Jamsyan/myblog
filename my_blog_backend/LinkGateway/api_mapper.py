import os
import json
import datetime
from typing import Dict, Any, List, Optional, Callable
from fastapi import APIRouter, Request, Response
from fastapi.routing import APIRoute
from .standards import APIStandard
from .logs import get_logger

class APIMapper:
    """
    API映射类，负责将所有引擎和业务的API接口映射到LinkGateway的对外接口
    """
    
    def __init__(self):
        """
        初始化API映射器
        """
        self.routers: Dict[str, APIRouter] = {}
        self.main_router = APIRouter()
        self.api_registry: Dict[str, Dict[str, Any]] = {}
        self.logger = get_logger("APIMapper")
        # 设置日志级别为INFO，减少不必要的调试日志
        self.logger.set_level("INFO")
        
        # 注册信息收集结构
        self.registered_apis = []
    
    def _normalize_path(self, path: str) -> str:
        """
        规范化路径格式
        
        Args:
            path: 原始路径
            
        Returns:
            str: 规范化后的路径
        """
        if not path:
            return ""
        # 确保路径以/开头
        if not path.startswith("/"):
            path = f"/{path}"
        # 移除末尾的/
        if path != "/" and path.endswith("/"):
            path = path[:-1]
        return path
    
    def _check_path_conflict(self, full_path: str, methods: list, service_id: str) -> bool:
        """
        检查API路径是否冲突
        
        Args:
            full_path: 完整的API路径
            methods: HTTP方法列表
            service_id: 服务ID
            
        Returns:
            bool: 是否存在冲突
        """
        if not isinstance(methods, list):
            methods = [methods] if isinstance(methods, str) else []
        
        if full_path in self.api_registry:
            existing_api = self.api_registry[full_path]
            existing_service = existing_api.get("service_id", "unknown")
            existing_methods = existing_api.get("methods", ["GET"])
            
            # 检查方法是否冲突
            conflicting_methods = set(methods) & set(existing_methods)
            if conflicting_methods:
                self.logger.log("WARNING", f"API路径冲突: {full_path}，方法: {conflicting_methods}，现有服务: {existing_service}，新服务: {service_id}", None)
                return True
        return False
    
    def create_router(self, service_id: str, api_prefix: str = "") -> APIRouter:
        """
        为服务创建一个API路由器
        
        Args:
            service_id: 服务ID
            api_prefix: API路由前缀
            
        Returns:
            APIRouter: 创建的API路由器
        """
        # 规范化前缀路径
        normalized_prefix = self._normalize_path(api_prefix)
        
        # 创建API路由器
        router = APIRouter(prefix=normalized_prefix)
        
        # 存储路由器
        self.routers[service_id] = router
        
        # 不要在这里将路由器挂载到主路由器，而是在map_service_apis中挂载
        
        return router
    
    def add_api_route(self, service_id: str, path: str, endpoint: Callable, **kwargs) -> bool:
        """
        为服务添加API路由
        
        Args:
            service_id: 服务ID
            path: 路由路径
            endpoint: 路由处理函数
            **kwargs: 额外的路由参数，包括description、tags、responses等
            
        Returns:
            bool: 添加成功返回True，失败返回False
        """
        try:
            # 检查服务是否有对应的路由器
            if service_id not in self.routers:
                self.create_router(service_id)
            
            # 获取路由器
            router = self.routers[service_id]
            
            # 规范化路径
            normalized_path = self._normalize_path(path)
            
            # 构建完整路径（避免重复拼接）
            if router.prefix:
                full_path = f"{router.prefix}{normalized_path}"
            else:
                full_path = normalized_path
            
            # 获取HTTP方法
            methods = kwargs.get("methods", ["GET"])
            if isinstance(methods, str):
                methods = [methods]
            methods = [m.upper() for m in methods]
            
            # 检查路径冲突
            if self._check_path_conflict(full_path, methods, service_id):
                self.logger.error(f"API路由添加失败，路径冲突: {full_path}")
                return False
            
            # 添加路由
            router.add_api_route(normalized_path, endpoint, **kwargs)
            
            # 注册详细的API信息
            api_info = {
                "service_id": service_id,
                "path": normalized_path,
                "full_path": full_path,
                "methods": methods,
                "endpoint": endpoint.__name__,
                "description": kwargs.get("description", ""),
                "tags": kwargs.get("tags", []),
                "responses": kwargs.get("responses", {}),
                "request_body": kwargs.get("request_body", None),
                "parameters": kwargs.get("parameters", []),
                "summary": kwargs.get("summary", ""),
                "registered_at": datetime.datetime.now().isoformat()
            }
            
            # 使用完整路径作为键
            self.api_registry[full_path] = api_info
            self.logger.log("DEBUG", f"API路由添加成功: {full_path}，服务: {service_id}", None)
            return True
        except Exception as e:
            self.logger.log("ERROR", f"添加API路由失败: {str(e)}", False)
            return False
    
    def map_business_apis(self, business_info: Dict[str, Any]) -> bool:
        """
        映射业务的API接口
        
        Args:
            business_info: 业务信息，包含业务的API定义
            
        Returns:
            bool: 映射成功返回True，失败返回False
        """
        try:
            service_id = business_info.get("service_id")
            business_path = business_info.get("business_path")
            
            if not service_id or not business_path:
                return False
            
            # 解析service.json文件，获取API定义
            service_json_path = os.path.join(business_path, "service.json")
            with open(service_json_path, "r", encoding="utf-8") as f:
                service_info = json.load(f)
            
            # 获取API定义
            apis = service_info.get("apis", [])
            
            # 使用API标准格式化前缀
            api_prefix = APIStandard.SERVICE_API_PREFIX.format(service_id=service_id)
            # 规范化前缀路径
            normalized_prefix = self._normalize_path(api_prefix)
            router = self.create_router(service_id, normalized_prefix)
            
            # 动态导入业务的路由模块
            router_module_path = os.path.join(business_path, "router.py")
            # 如果router.py不存在，尝试使用api.py
            if not os.path.exists(router_module_path):
                router_module_path = os.path.join(business_path, "api.py")
            
            if os.path.exists(router_module_path):
                # 这里需要实现动态导入和路由注册的逻辑
                # 由于Python的导入机制，需要使用importlib来动态导入模块
                import importlib.util
                import sys
                
                # 保存原始sys.path，以便后续恢复
                original_sys_path = sys.path.copy()
                
                try:
                    
                    # 创建一个隔离的sys.path，只包含业务服务目录和必要的系统路径
                    isolated_sys_path = [business_path]
                    # 添加必要的系统路径，确保基本模块可用
                    for path in sys.path:
                        if path and (path.startswith(sys.prefix) or 'site-packages' in path or 'Lib' in path):
                            isolated_sys_path.append(path)
                    
                    # 临时替换sys.path
                    sys.path = isolated_sys_path
                    
                    # 动态导入模块
                    spec = importlib.util.spec_from_file_location(f"{service_id}_router", router_module_path)
                    if spec and spec.loader:
                        router_module = importlib.util.module_from_spec(spec)
                        # 设置模块的__file__属性，确保相对导入正常工作
                        router_module.__file__ = router_module_path
                        # 设置模块的__package__属性
                        router_module.__package__ = f"services.{service_id}"
                        spec.loader.exec_module(router_module)
                        
                        # 检查模块中是否有setup_router函数
                        if hasattr(router_module, "setup_router"):
                            # 调用setup_router函数，传入路由器和API定义
                            setup_router_func = getattr(router_module, "setup_router")
                            
                            # 检查setup_router函数的参数数量，支持传入API定义和db_link
                            import inspect
                            sig = inspect.signature(setup_router_func)
                            
                            # 从全局作用域获取db_link_manager实例
                            db_link = None
                            try:
                                if hasattr(sys.modules['__main__'], 'gateway'):
                                    db_link = sys.modules['__main__'].gateway.db_link
                                else:
                                    # 尝试从父模块获取gateway实例
                                    from LinkGateway.gateway import LinkGateway
                                    import gc
                                    for obj in gc.get_objects():
                                        if isinstance(obj, LinkGateway):
                                            db_link = obj.db_link
                                            break
                            except Exception as e:
                                self.logger.log("WARNING", f"获取db_link失败: {str(e)}", None)
                            
                            try:
                                if len(sig.parameters) >= 3:
                                    # 如果setup_router函数接受第三个参数，传入db_link
                                    setup_router_func(router, apis, db_link)
                                elif len(sig.parameters) >= 2:
                                    # 如果setup_router函数接受第二个参数，传入API定义
                                    setup_router_func(router, apis)
                                else:
                                    # 否则只传入路由器
                                    setup_router_func(router)
                            except Exception as e:
                                self.logger.error(f"调用setup_router失败: {str(e)}")
                        else:
                            # 如果模块中没有setup_router函数，尝试直接获取router对象
                            if hasattr(router_module, "router"):
                                # 将路由模块中定义的路由添加到路由器中
                                module_router = getattr(router_module, "router")
                                for route in module_router.routes:
                                    # 确保是APIRoute对象
                                    from fastapi.routing import APIRoute
                                    if isinstance(route, APIRoute):
                                        # 添加路由到当前路由器
                                        try:
                                            router.add_api_route(
                                                path=route.path,
                                                endpoint=route.endpoint,
                                                methods=route.methods,
                                                name=route.name,
                                                description=route.description if hasattr(route, "description") else None,
                                                tags=route.tags if hasattr(route, "tags") else [service_id],
                                                responses=route.responses if hasattr(route, "responses") else {},
                                                summary=route.summary if hasattr(route, "summary") else None
                                            )
                                        except Exception as e:
                                            self.logger.error(f"添加路由失败: {str(e)}")
                except Exception as e:
                    self.logger.error(f"动态导入模块失败: {str(e)}")
                finally:
                    # 恢复原始sys.path，避免影响其他模块的导入
                    sys.path = original_sys_path
            
            # 获取路由器中定义的所有路由，并添加到api_registry中
            if service_id in self.routers:
                router = self.routers[service_id]
                
                # 检查路由器是否已经有路由
                if router.routes:
                    # 如果路由器已经有路由，说明setup_router()已经注册过，跳过从service.json重复注册
                    self.logger.log("DEBUG", f"路由器已有路由，跳过从service.json重复注册: {service_id}", None)
                else:
                    # 路由器为空，才从service.json中注册路由
                    for route in router.routes:
                        # 确保是APIRoute对象
                        from fastapi.routing import APIRoute
                        if isinstance(route, APIRoute):
                            path = route.path
                            methods = list(route.methods)
                            description = route.description if hasattr(route, "description") else ""
                            tags = [service_id]
                            
                            # 构建完整路径（route.path已经包含了路由器前缀，无需重复添加）
                            normalized_path = self._normalize_path(path)
                            full_path = normalized_path
                            
                            # 检查路径冲突
                            if not self._check_path_conflict(full_path, methods, service_id):
                                # 注册API信息
                                api_info = {
                                    "service_id": service_id,
                                    "path": normalized_path,
                                    "full_path": full_path,
                                    "methods": methods,
                                    "endpoint": route.name if hasattr(route, "name") else "",
                                    "description": description,
                                    "tags": tags,
                                    "responses": {},
                                    "request_body": None,
                                    "parameters": [],
                                    "summary": route.summary if hasattr(route, "summary") else description.split(".")[0] if description else "",
                                    "registered_at": datetime.datetime.now().isoformat()
                                }
                                
                                self.api_registry[full_path] = api_info
                                
                                # 将注册成功的API信息添加到收集结构
                                api_register_info = {
                                    'service_id': service_id,
                                    'path': full_path,
                                    'methods': methods,
                                    'endpoint': api_info.get('endpoint')
                                }
                                self.registered_apis.append(api_register_info)
                            
                            self.logger.log("DEBUG", f"API路由添加成功: {full_path}，服务: {service_id}", None)
                        else:
                            self.logger.log("WARNING", f"跳过重复API路由: {full_path}，服务: {service_id}", None)
            
            # 将路由器挂载到主路由器
            if service_id in self.routers:
                self.main_router.include_router(self.routers[service_id])
            
            return True
        except Exception as e:
            self.logger.error(f"映射业务API失败，服务ID: {service_id}，错误: {str(e)}")
            return False
    
    async def forward_request(self, request: Request, service_id: str) -> Any:
        """
        转发请求到对应的服务
        
        Args:
            request: FastAPI请求对象
            service_id: 目标服务ID
            
        Returns:
            Any: 请求处理结果
        """
        try:
            registry = self._get_registry()
            if not registry:
                return {"error": "Service registry not initialized", "status": "error"}
            
            service = registry.get_service(service_id)
            if not service:
                return {"error": "Service not found", "status": "error", "service_id": service_id}
            
            service_type = service.get("type")
            
            if service_type == "engine" and service_id in registry.engines:
                engine = registry.engines[service_id]
                path = request.url.path
                action = path.split("/")[-1] if path else ""
                
                try:
                    body = await request.json()
                except:
                    body = {}
                
                params = {
                    **dict(request.path_params),
                    **dict(request.query_params)
                }
                
                request_data = {
                    "action": action,
                    "params": params,
                    "body": body
                }
                
                try:
                    result = engine.handle_request(action, request_data)
                    return result
                except Exception as e:
                    self.logger.log("ERROR", f"调用引擎 {service_id} 失败: {str(e)}", False)
                    return {"error": f"Engine call failed: {str(e)}", "status": "error"}
            else:
                self.logger.log("ERROR", f"服务 {service_id} 不是引擎服务或不存在", False)
                return {"error": "Service not found or not an engine", "status": "error"}
        except Exception as e:
            self.logger.log("ERROR", f"转发请求失败: {str(e)}", False)
            return {"error": f"Request forwarding failed: {str(e)}", "status": "error"}
    
    def _get_registry(self):
        """
        获取服务注册表实例
        
        Returns:
            ServiceRegistry: 服务注册表实例，未找到返回None
        """
        try:
            import sys
            if hasattr(sys.modules['__main__'], 'gateway'):
                return sys.modules['__main__'].gateway.registry
            else:
                from LinkGateway.gateway import LinkGateway
                import gc
                for obj in gc.get_objects():
                    if isinstance(obj, LinkGateway):
                        return obj.registry
        except Exception as e:
            self.logger.log("ERROR", f"获取服务注册表失败: {str(e)}", False)
        return None
    
    def create_proxy_endpoint(self, service_id: str, action: str) -> Callable:
        """
        创建代理端点，用于转发请求到对应的服务
        
        Args:
            service_id: 目标服务ID
            action: 请求动作
            
        Returns:
            Callable: 代理端点函数
        """
        async def proxy_endpoint(request: Request, **kwargs):
            """
            代理端点函数，用于转发请求
            """
            try:
                # 获取请求数据
                try:
                    body = await request.json()
                except:
                    body = {}
                
                # 合并路径参数和查询参数
                params = {
                    **kwargs,
                    **dict(request.query_params)
                }
                
                # 构建请求数据
                request_data = {
                    "action": action,
                    "params": params,
                    "body": body
                }
                
                # 转发请求
                result = await self.forward_request(request, service_id)
                
                return result
            except Exception as e:
                self.logger.log("ERROR", f"代理端点处理请求失败: {str(e)}", False)
                return {"error": f"Proxy endpoint failed: {str(e)}", "status": "error"}
        
        return proxy_endpoint
    
    def map_all_apis(self, services: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        映射所有服务的API接口
        
        Args:
            services: 服务列表
            
        Returns:
            Dict[str, Any]: 映射结果，包含成功和失败的服务信息
        """
        result = {
            "success": [],
            "failed": []
        }
        
        self.registered_apis.clear()
        
        for service in services:
            service_id = service["service_id"]
            service_type = service["type"]
            info = service["info"]
            
            try:
                if service_type == "business":
                    self._map_business_service(service_id, info, result)
                elif service_type == "engine":
                    self._map_engine_service(service_id, info, result)
            except Exception as e:
                self.logger.error(f"映射API失败，服务ID: {service_id}，错误: {str(e)}")
                result["failed"].append(service_id)
        
        self.logger.info(f"API映射完成，成功: {len(result['success'])}, 失败: {len(result['failed'])}")
        self._log_api_mapping_summary()
        
        return result
    
    def _map_business_service(self, service_id: str, info: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        映射业务服务API
        
        Args:
            service_id: 服务ID
            info: 服务信息
            result: 映射结果
        """
        if self.map_business_apis(info):
            self.logger.log("INFO", f"映射业务API，服务ID: {service_id}", True)
            result["success"].append(service_id)
        else:
            result["failed"].append(service_id)
    
    def _map_engine_service(self, service_id: str, info: Dict[str, Any], result: Dict[str, Any]) -> None:
        """
        映射引擎服务API
        
        Args:
            service_id: 服务ID
            info: 服务信息
            result: 映射结果
        """
        self.logger.info(f"映射引擎API到文档，服务ID: {service_id}")
        apis = info.get("apis", [])
        
        api_prefix = APIStandard.ENGINE_API_PREFIX.format(engine_name=service_id)
        normalized_prefix = self._normalize_path(api_prefix)
        router = self.create_router(service_id, normalized_prefix)
        
        for api in apis:
            self._register_engine_api(service_id, api, normalized_prefix, router)
        
        result["success"].append(service_id)
    
    def _register_engine_api(self, service_id: str, api: Dict[str, Any], normalized_prefix: str, router: APIRouter) -> None:
        """
        注册引擎API
        
        Args:
            service_id: 服务ID
            api: API定义
            normalized_prefix: 规范化前缀
            router: 路由器
        """
        path = api.get("path", "")
        method = api.get("method", "GET").upper()
        description = api.get("description", "")
        tags = api.get("tags", [service_id])
        
        normalized_path = self._normalize_path(path)
        full_path = f"{normalized_prefix}{normalized_path}"
        
        if self._check_path_conflict(full_path, [method], service_id):
            self.logger.warning(f"跳过重复引擎API路由: {full_path}，服务: {service_id}")
            return
        
        api_info = self._build_api_info(service_id, normalized_path, full_path, method, description, tags, api)
        self.api_registry[full_path] = api_info
        
        api_register_info = {
            'service_id': service_id,
            'path': full_path,
            'methods': [method],
            'endpoint': api_info.get('endpoint')
        }
        self.registered_apis.append(api_register_info)
        
        self.logger.debug(f"引擎API路由添加成功: {full_path}，服务: {service_id}")
    
    def _build_api_info(self, service_id: str, normalized_path: str, full_path: str, method: str, description: str, tags: List[str], api: Dict[str, Any]) -> Dict[str, Any]:
        """
        构建API信息
        
        Args:
            service_id: 服务ID
            normalized_path: 规范化路径
            full_path: 完整路径
            method: HTTP方法
            description: 描述
            tags: 标签
            api: API定义
            
        Returns:
            Dict[str, Any]: API信息
        """
        return {
            "service_id": service_id,
            "path": normalized_path,
            "full_path": full_path,
            "methods": [method],
            "endpoint": "default_endpoint",
            "description": description,
            "tags": tags,
            "responses": api.get("responses", {}),
            "request_body": api.get("request_body", None),
            "parameters": api.get("parameters", []),
            "summary": api.get("summary", description.split(".")[0] if description else ""),
            "registered_at": datetime.datetime.now().isoformat()
        }
    
    def _log_api_mapping_summary(self) -> None:
        """
        输出API映射摘要
        """
        if not self.registered_apis:
            return
        
        self.logger.info(f"  - 注册成功的API：{len(self.registered_apis)} 个")
        api_by_service = {}
        
        for api_info in self.registered_apis:
            service_id = api_info.get('service_id')
            if service_id not in api_by_service:
                api_by_service[service_id] = 0
            api_by_service[service_id] += 1
        
        for service_id, api_count in api_by_service.items():
            self.logger.info(f"    - 服务 {service_id}：{api_count} 个API")
    
    def get_api_info(self, path: str, method: str = "GET") -> Optional[Dict[str, Any]]:
        """
        获取API信息
        
        Args:
            path: API路径
            method: HTTP方法
            
        Returns:
            Optional[Dict[str, Any]]: API信息，未找到返回None
        """
        # 查找API信息
        api_info = self.api_registry.get(path)
        if api_info and method in api_info["methods"]:
            return api_info
        
        return None
    
    def list_apis(self) -> List[Dict[str, Any]]:
        """
        列出所有注册的API
        
        Returns:
            List[Dict[str, Any]]: API列表
        """
        return list(self.api_registry.values())
    
    def clear_apis(self) -> None:
        """
        清除所有注册的API
        """
        # 清空路由器
        self.routers.clear()
        
        # 重新创建主路由器
        self.main_router = APIRouter()
        
        # 清空API注册表
        self.api_registry.clear()
    
    def get_main_router(self) -> APIRouter:
        """
        获取主路由器，用于挂载到FastAPI应用
        
        Returns:
            APIRouter: 主路由器
        """
        return self.main_router