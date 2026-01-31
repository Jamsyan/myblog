import os
import sys
import uuid
import logging
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .registry import ServiceRegistry
from .db_link import DatabaseLinkManager
from .api_mapper import APIMapper
from .inner_comm import InnerCommunicator
from .outer_comm import OuterCommunicator
from .auth import AuthManager
from .logs import get_logger
from .path_manager import PathManager
from .service_proxy import ServiceProxy
from .dependency_injector import DependencyInjector

class LinkGateway:
    """
    LinkGateway核心类，作为整个通信核心的枢纽，协调各个组件的工作
    """
    
    def __init__(self, base_path: str, debug: bool = False):
        """
        初始化LinkGateway
        
        Args:
            base_path: 项目根目录路径
            debug: 是否启用调试模式
        """
        self.base_path = base_path
        self.debug = debug
        
        # 初始化路径管理器，用于获取日志路径
        self.path_manager = PathManager(base_path)
        
        # 配置日志，设置日志文件路径
        log_path = self.path_manager.get_linkgateway_log_path()
        self.logger = get_logger("LinkGateway", log_path)
        self.logger.set_level("DEBUG" if debug else "INFO")
        # 生成实例ID，用于标识当前LinkGateway实例
        self.instance_id = str(uuid.uuid4())[:8]
        
        try:
            self.logger.log_progress("正在初始化核心组件", service_id="LinkGateway", request_id=self.instance_id)
            
            self.registry = ServiceRegistry(base_path)
            self.db_link = DatabaseLinkManager(base_path)
            self.api_mapper = APIMapper()
            self.inner_comm = InnerCommunicator()
            self.outer_comm = OuterCommunicator()
            self.auth_manager = AuthManager()
            
            self.service_proxy = ServiceProxy(self.registry)
            
            from .plugin import PluginManager
            self.plugin_manager = PluginManager(self)
            
            self.dependency_injector = DependencyInjector(self)
            
            self.app = FastAPI(
                title="LinkGateway API",
                description="Backend micro-service architecture core communication component. \n\n"+
                "LinkGateway provides service discovery, API mapping, and service-to-service communication for the micro-service ecosystem.\n\n"+
                "## API Layers\n"+
                "- **Core API**: System-level functionality like service management and health checks\n"+
                "- **Engine API**: Common functionality provided by engine services\n"+
                "- **Business API**: Business logic provided by business services",
                version="1.0.0",
                docs_url="/docs",
                redoc_url="/redoc",
                openapi_url="/api-docs/openapi.json"
            )
            
            self._configure_cors()
            
            self._register_default_routes()
            
            self._register_proxy_routes()
            
            self._register_plugin_middleware()
            
            self.logger.log("INFO", "LinkGateway初始化", True, service_id="LinkGateway", request_id=self.instance_id)
        except Exception as e:
            self.logger.log("ERROR", f"LinkGateway初始化: {str(e)}", False, service_id="LinkGateway", request_id=self.instance_id)
            raise
    
    def _configure_cors(self) -> None:
        """
        配置CORS中间件，允许前端跨域访问
        """
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:5173",
                "http://localhost:3000",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:3000",
                "*"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.logger.debug("CORS中间件已配置", service_id="LinkGateway", request_id=self.instance_id)
    
    def _register_default_routes(self) -> None:
        """
        注册默认路由
        """
        @self.app.get("/")
        async def root():
            return {
                "message": "LinkGateway is running",
                "status": "ok",
                "version": "1.0.0"
            }
        
        @self.app.get("/health")
        async def health_check():
            # 检查所有服务的健康状态
            health_result = self.registry.check_all_services_health()
            return {
                "status": "ok",
                "total_services": len(health_result["healthy"]) + len(health_result["unhealthy"]),
                "healthy_services": len(health_result["healthy"]),
                "unhealthy_services": len(health_result["unhealthy"]),
                "services": health_result
            }
        
        @self.app.get("/services")
        async def list_services():
            return self.registry.list_services()
        
        @self.app.get("/services/{service_id}")
        async def get_service(service_id: str):
            service = self.registry.get_service(service_id)
            if not service:
                return {
                    "error": "Service not found",
                    "service_id": service_id
                }
            return service
        
        @self.app.get("/services/{service_id}/health")
        async def check_service_health_endpoint(service_id: str):
            """
            检查单个服务的健康状态
            """
            is_healthy = self.registry.check_service_health(service_id)
            return {
                "service_id": service_id,
                "status": "healthy" if is_healthy else "unhealthy"
            }
        
        @self.app.post("/services/reload")
        async def reload_services():
            """
            重新加载所有服务
            """
            result = self.registry.reload_services()
            return {
                "status": "ok",
                "result": result
            }
        
        @self.app.get("/apis")
        async def list_apis():
            """
            列出所有已注册的 API 端点
            """
            return self.api_mapper.list_apis()
        
        @self.app.get("/api-docs")
        async def api_docs():
            """
            获取 API 文档概览信息
            """
            return {
                "title": self.app.title,
                "description": self.app.description,
                "version": self.app.version,
                "docs_url": "/docs",
                "redoc_url": "/redoc",
                "openapi_url": "/api-docs/openapi.json",
                "api_layers": [
                    {
                        "name": "Core API",
                        "description": "System-level functionality like service management and health checks",
                        "endpoints": [
                            "/",
                            "/health",
                            "/services",
                            "/services/{service_id}",
                            "/services/{service_id}/health",
                            "/services/reload",
                            "/apis",
                            "/routes",
                            "/interaction-rule"
                        ]
                    },
                    {
                        "name": "Engine API",
                        "description": "Common functionality provided by engine services",
                        "endpoints": []
                    },
                    {
                        "name": "Business API",
                        "description": "Business logic provided by business services",
                        "endpoints": []
                    }
                ]
            }
        
        @self.app.get("/routes")
        async def list_routes():
            from fastapi.routing import APIRoute
            routes = []
            for route in self.app.routes:
                if isinstance(route, APIRoute):
                    routes.append({
                        "path": route.path,
                        "name": route.name,
                        "methods": list(route.methods)
                    })
            return routes
        
        @self.app.get("/interaction-rule")
        async def get_interaction_rule():
            """
            获取服务交互规则
            """
            return {
                "rules": [
                    "业务服务可以调用引擎服务",
                    "引擎服务不能直接相互调用",
                    "引擎服务可以被业务服务调用",
                    "服务只能通过LinkGateway调用对应的服务"
                ]
            }
    
    def start(self, host: str = "0.0.0.0", port: int = 8000) -> None:
        """
        启动LinkGateway
        
        Args:
            host: 主机地址
            port: 端口号
        """
        request_id = str(uuid.uuid4())[:8]
        
        self.logger.enable_structured_output()
        
        try:
            if not self._check_port_available(host, port):
                error_msg = f"端口 {port} 已被占用，请检查是否有其他进程正在运行"
                self.logger.log("ERROR", error_msg, False, service_id="LinkGateway", request_id=request_id)
                raise RuntimeError(error_msg)
            
            self.logger.log_progress("加载插件", service_id="LinkGateway", request_id=request_id)
            plugin_result = self.plugin_manager.load_plugins()
            
            self.logger.log_progress("发现服务", service_id="LinkGateway", request_id=request_id)
            service_result = self.discover_services()
            
            self.logger.log_progress("映射API", service_id="LinkGateway", request_id=request_id)
            api_result = self.map_apis()
            
            import uvicorn
            from .logs import UvicornLogHandler
            
            self.logger.log("INFO", f"启动FastAPI服务在{host}:{port}", True, service_id="LinkGateway", request_id=request_id)
            
            # 配置 uvicorn 使用我们的日志处理器（在 uvicorn.run 之前配置）
            uvicorn_logger = logging.getLogger("uvicorn")
            uvicorn_logger.setLevel(logging.INFO)
            uvicorn_logger.handlers.clear()
            uvicorn_logger.propagate = False
            uvicorn_logger.addHandler(UvicornLogHandler(self.logger))
            
            uvicorn_access_logger = logging.getLogger("uvicorn.access")
            uvicorn_access_logger.setLevel(logging.INFO)
            uvicorn_access_logger.handlers.clear()
            uvicorn_access_logger.propagate = False
            uvicorn_access_logger.addHandler(UvicornLogHandler(self.logger))
            
            uvicorn.run(
                self.app, 
                host=host, 
                port=port,
                log_level="info",
                access_log=True,
                use_colors=True
            )
        except Exception as e:
            self.logger.error(f"LinkGateway启动失败: {str(e)}", service_id="LinkGateway", request_id=request_id)
            # 尝试优雅关闭
            try:
                self.shutdown()
            except:
                pass
            raise
    
    def _check_port_available(self, host: str, port: int) -> bool:
        """
        检查端口是否可用
        
        Args:
            host: 主机地址
            port: 端口号
            
        Returns:
            bool: 端口可用返回True，否则返回False
        """
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                if result == 0:
                    return False
                return True
        except Exception as e:
            self.logger.log("WARNING", f"端口检查: {str(e)}", False)
            return True
    
    def discover_services(self) -> Dict[str, Any]:
        """
        发现所有服务
        
        Returns:
            Dict[str, Any]: 发现结果
        """
        request_id = str(uuid.uuid4())[:8]
        
        try:
            result = self.registry.discover_services()
            
            if not self._validate_discovery_result(result, request_id):
                return self._get_default_discovery_result()
            
            self._extract_discovery_summary(result)
            self._create_business_db_connections(result, request_id)
            self._register_engines_to_inner_comm(result, request_id)
            
            total_services = result.get("total_services", 0)
            self.logger.info(f"服务发现流程完成，共发现 {total_services} 个服务", service_id="LinkGateway", request_id=request_id)
            return result
        except Exception as e:
            self.logger.log("ERROR", f"服务发现: {str(e)}", False, service_id="LinkGateway", request_id=request_id)
            return self._get_default_discovery_result()
    
    def _validate_discovery_result(self, result: Any, request_id: str) -> bool:
        """
        验证发现结果格式
        
        Args:
            result: 发现结果
            request_id: 请求ID
            
        Returns:
            bool: 验证通过返回True
        """
        if not isinstance(result, dict):
            self.logger.error("服务发现结果格式错误", service_id="LinkGateway", request_id=request_id)
            return False
        return True
    
    def _get_default_discovery_result(self) -> Dict[str, Any]:
        """
        获取默认的发现结果
        
        Returns:
            Dict[str, Any]: 默认结果
        """
        return {
            "businesses": [],
            "engines": [],
            "total_services": 0,
            "summary": {
                "businesses": {"valid": 0, "invalid": 0},
                "engines": {"valid": 0, "invalid": 0}
            }
        }
    
    def _extract_discovery_summary(self, result: Dict[str, Any]) -> None:
        """
        提取发现结果摘要
        
        Args:
            result: 发现结果
        """
        business_count = len(result.get("businesses", []))
        engine_count = len(result.get("engines", []))
        result["total_services"] = business_count + engine_count
        
        if "summary" not in result:
            valid_businesses = sum(1 for b in result.get("businesses", []) if b.get("status") == "valid")
            invalid_businesses = business_count - valid_businesses
            valid_engines = sum(1 for e in result.get("engines", []) if e.get("status") == "valid")
            invalid_engines = engine_count - valid_engines
            
            result["summary"] = {
                "businesses": {"valid": valid_businesses, "invalid": invalid_businesses},
                "engines": {"valid": valid_engines, "invalid": invalid_engines}
            }
    
    def _create_business_db_connections(self, result: Dict[str, Any], request_id: str) -> None:
        """
        为有效业务服务创建数据库连接
        
        Args:
            result: 发现结果
            request_id: 请求ID
        """
        self.logger.debug("正在为有效业务服务创建数据库连接...", service_id="LinkGateway", request_id=request_id)
        
        for business in result.get("businesses", []):
            if business.get("status") != "valid":
                continue
            
            service_id = business.get("service_id")
            db_config = business.get("database")
            
            if not service_id or not db_config:
                continue
            
            try:
                self.db_link.create_connection(service_id, db_config)
                self.logger.debug(f"  - 已为业务服务 {service_id} 创建数据库连接", service_id="LinkGateway", request_id=request_id)
            except Exception as e:
                self.logger.error(f"为业务服务 {service_id} 创建数据库连接失败: {str(e)}", service_id="LinkGateway", request_id=request_id)
    
    def _register_engines_to_inner_comm(self, result: Dict[str, Any], request_id: str) -> None:
        """
        将引擎注册到 InnerCommunicator
        
        Args:
            result: 发现结果
            request_id: 请求ID
        """
        self.logger.debug("正在将引擎注册到 InnerCommunicator...", service_id="LinkGateway", request_id=request_id)
        
        for engine_id, engine in self.registry.engines.items():
            try:
                engine._allow_direct_call = True
                self.inner_comm.register_engine(engine_id, engine)
                self.logger.debug(f"  - 已将引擎 {engine_id} 注册到 InnerCommunicator", service_id="LinkGateway", request_id=request_id)
            except Exception as e:
                self.logger.error(f"将引擎 {engine_id} 注册到 InnerCommunicator 失败: {str(e)}", service_id="LinkGateway", request_id=request_id)
    
    def map_apis(self) -> Dict[str, Any]:
        """
        映射所有API
        只对外暴露业务服务的API，引擎API通过内部代理访问
        
        Returns:
            Dict[str, Any]: 映射结果
        """
        request_id = str(uuid.uuid4())[:8]
        self.logger.info("正在映射API...", service_id="LinkGateway", request_id=request_id)
        
        try:
            # 清空之前的API映射
            self.api_mapper.clear_apis()
            
            # 获取所有服务
            services = self.registry.list_services()
            if not isinstance(services, list):
                self.logger.error("服务列表格式错误", service_id="LinkGateway", request_id=request_id)
                return {"success": [], "failed": []}
            
            # 映射API
            result = self.api_mapper.map_all_apis(services)
            
            # 验证结果格式
            if not isinstance(result, dict):
                self.logger.error("API映射结果格式错误", service_id="LinkGateway", request_id=request_id)
                return {"success": [], "failed": []}
            
            # 将主路由器挂载到FastAPI应用
            # 只挂载业务服务的API路由器
            try:
                self.app.include_router(self.api_mapper.get_main_router())
            except Exception as e:
                self.logger.error(f"挂载API路由器失败: {str(e)}", service_id="LinkGateway", request_id=request_id)
            
            self.logger.info(f"API映射完成。成功: {len(result.get('success', []))}, 失败: {len(result.get('failed', []))}", service_id="LinkGateway", request_id=request_id)
            api_count = len(self.api_mapper.api_registry)
            self.logger.info(f"对外暴露的API路由数量: {api_count}", service_id="LinkGateway", request_id=request_id)
            
            # 只在DEBUG级别下输出详细的API路由信息
            if self.debug:
                self.logger.debug("对外暴露的API路由详细信息:", service_id="LinkGateway", request_id=request_id)
                for full_path, api_info in self.api_mapper.api_registry.items():
                    service_id = api_info.get('service_id', 'unknown')
                    methods = ','.join(api_info.get('methods', ['GET']))
                    summary = api_info.get('summary', '')
                    self.logger.debug(f"  [{service_id}] {methods} {full_path} - {summary}", service_id="LinkGateway", request_id=request_id)
            
            return result
        except Exception as e:
            self.logger.log("ERROR", f"API映射: {str(e)}", False, service_id="LinkGateway", request_id=request_id)
            # 返回默认结果，确保系统不会因为API映射失败而崩溃
            return {"success": [], "failed": []}
    
    def register_engine(self, engine: Any) -> bool:
        """
        注册引擎
        
        Args:
            engine: 引擎实例
            
        Returns:
            bool: 注册成功返回True，失败返回False
            
        Note:
            此方法保留用于未来扩展，当前引擎注册由ServiceRegistry自动处理
        """
        raise NotImplementedError("Engine registration is handled automatically by ServiceRegistry")
    
    def register_business(self, business_info: Dict[str, Any]) -> bool:
        """
        注册业务
        
        Args:
            business_info: 业务信息
            
        Returns:
            bool: 注册成功返回True，失败返回False
            
        Note:
            此方法保留用于未来扩展，当前业务注册由ServiceRegistry自动处理
        """
        raise NotImplementedError("Business registration is handled automatically by ServiceRegistry")
    
    def get_app(self) -> FastAPI:
        """
        获取FastAPI应用
        
        Returns:
            FastAPI: FastAPI应用实例
        """
        return self.app
    
    def shutdown(self) -> None:
        """
        关闭LinkGateway，释放资源
        """
        request_id = str(uuid.uuid4())[:8]
        self.logger.info("正在关闭LinkGateway...", service_id="LinkGateway", request_id=request_id)
        
        # 关闭所有插件
        self.logger.info("正在关闭插件...", service_id="LinkGateway", request_id=request_id)
        self.plugin_manager.shutdown_plugins()
        
        # 断开所有数据库连接
        self.db_link.disconnect_all()
        
        self.logger.log("INFO", "LinkGateway关闭", True, service_id="LinkGateway", request_id=request_id)
    
    def add_middleware(self, middleware: Any, **kwargs) -> None:
        """
        添加中间件
        
        Args:
            middleware: 中间件类
            **kwargs: 中间件参数
        """
        self.app.add_middleware(middleware, **kwargs)
    
    def include_router(self, router: Any, **kwargs) -> None:
        """
        包含路由器
        
        Args:
            router: 路由器实例
            **kwargs: 路由器参数
        """
        self.app.include_router(router, **kwargs)
    
    def _register_proxy_routes(self) -> None:
        """
        注册服务代理路由
        """
        # 获取服务代理路由器
        proxy_router = self.service_proxy.get_router()
        
        # 注册服务代理路由
        self.app.include_router(proxy_router)
    
    def _register_plugin_middleware(self) -> None:
        """
        注册插件中间件
        """
        @self.app.middleware("http")
        async def plugin_middleware(request: Request, call_next):
            # 通知插件请求进入
            plugin_response = self.plugin_manager.notify_request_incoming(request)
            if plugin_response is not None:
                return plugin_response
            
            # 继续处理请求
            response = await call_next(request)
            
            # 通知插件响应返回
            plugin_response = self.plugin_manager.notify_response_outgoing(response)
            if plugin_response is not None:
                return plugin_response
            
            return response
    
    def mount(self, path: str, app: Any, **kwargs) -> None:
        """
        挂载子应用
        
        Args:
            path: 挂载路径
            app: 子应用实例
            **kwargs: 挂载参数
        """
        self.app.mount(path, app, **kwargs)
