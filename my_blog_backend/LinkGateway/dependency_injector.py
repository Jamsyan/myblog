from typing import Dict, Any, Optional


class DependencyInjector:
    """
    依赖注入器
    管理所有核心组件，提供类型安全的访问方法
    """
    
    def __init__(self, gateway: Any):
        """
        初始化依赖注入器
        
        Args:
            gateway: LinkGateway 实例
        """
        self._services: Dict[str, Any] = {}
        
        # 注册核心组件
        self._register_service('gateway', gateway)
        self._register_service('registry', gateway.registry)
        self._register_service('api_mapper', gateway.api_mapper)
        self._register_service('service_proxy', gateway.service_proxy)
        self._register_service('plugin_manager', gateway.plugin_manager)
        self._register_service('inner_comm', gateway.inner_comm)
        self._register_service('outer_comm', gateway.outer_comm)
        self._register_service('db_link', gateway.db_link)
        self._register_service('auth_manager', gateway.auth_manager)
        self._register_service('path_manager', gateway.path_manager)
        self._register_service('logger', gateway.logger)
    
    def _register_service(self, name: str, instance: Any) -> None:
        """
        注册服务
        
        Args:
            name: 服务名称
            instance: 服务实例
        """
        self._services[name] = instance
    
    def register(self, name: str, instance: Any) -> None:
        """
        注册新服务
        
        Args:
            name: 服务名称
            instance: 服务实例
        """
        self._register_service(name, instance)
    
    def get(self, name: str) -> Optional[Any]:
        """
        获取服务实例
        
        Args:
            name: 服务名称
            
        Returns:
            Optional[Any]: 服务实例，未找到返回None
        """
        return self._services.get(name)
    
    def get_registry(self):
        """
        获取服务注册表
        
        Returns:
            ServiceRegistry: 服务注册表实例
        """
        return self.get('registry')
    
    def get_api_mapper(self):
        """
        获取 API 映射器
        
        Returns:
            APIMapper: API 映射器实例
        """
        return self.get('api_mapper')
    
    def get_service_proxy(self):
        """
        获取服务代理
        
        Returns:
            ServiceProxy: 服务代理实例
        """
        return self.get('service_proxy')
    
    def get_plugin_manager(self):
        """
        获取插件管理器
        
        Returns:
            PluginManager: 插件管理器实例
        """
        return self.get('plugin_manager')
    
    def get_inner_comm(self):
        """
        获取内部通信器
        
        Returns:
            InnerCommunicator: 内部通信器实例
        """
        return self.get('inner_comm')
    
    def get_outer_comm(self):
        """
        获取外部通信器
        
        Returns:
            OuterCommunicator: 外部通信器实例
        """
        return self.get('outer_comm')
    
    def get_db_link(self):
        """
        获取数据库链接管理器
        
        Returns:
            DatabaseLinkManager: 数据库链接管理器实例
        """
        return self.get('db_link')
    
    def get_auth_manager(self):
        """
        获取认证管理器
        
        Returns:
            AuthManager: 认证管理器实例
        """
        return self.get('auth_manager')
    
    def get_path_manager(self):
        """
        获取路径管理器
        
        Returns:
            PathManager: 路径管理器实例
        """
        return self.get('path_manager')
    
    def get_logger(self):
        """
        获取日志记录器
        
        Returns:
            Logger: 日志记录器实例
        """
        return self.get('logger')
    
    def list_services(self) -> Dict[str, Any]:
        """
        列出所有已注册的服务
        
        Returns:
            Dict[str, Any]: 服务字典
        """
        return self._services.copy()
    
    def has_service(self, name: str) -> bool:
        """
        检查服务是否已注册
        
        Args:
            name: 服务名称
            
        Returns:
            bool: 已注册返回True，否则返回False
        """
        return name in self._services