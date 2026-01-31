from typing import Dict, Any, Callable, List, Optional
import os
import importlib.util
from .logs import get_logger


class Plugin:
    """
    插件基类，所有插件都需要继承这个类
    """
    
    # 插件状态枚举
    class Status:
        INITIALIZED = "initialized"
        RUNNING = "running"
        STOPPED = "stopped"
        ERROR = "error"
    
    def __init__(self, gateway):
        """
        初始化插件
        
        Args:
            gateway: LinkGateway实例
        """
        self.gateway = gateway
        self.logger = get_logger(f"Plugin.{self.__class__.__name__}", gateway.path_manager.get_linkgateway_log_path())
        self.status = self.Status.INITIALIZED
        self.dependencies = []  # 插件依赖列表
        
        # 提供核心组件的便捷访问
        self.registry = gateway.dependency_injector.get_registry()
        self.api_mapper = gateway.dependency_injector.get_api_mapper()
        self.service_proxy = gateway.dependency_injector.get_service_proxy()
        self.plugin_manager = gateway.dependency_injector.get_plugin_manager()
        self.inner_comm = gateway.dependency_injector.get_inner_comm()
        self.outer_comm = gateway.dependency_injector.get_outer_comm()
        self.db_link = gateway.dependency_injector.get_db_link()
        self.auth_manager = gateway.dependency_injector.get_auth_manager()
        self.path_manager = gateway.dependency_injector.get_path_manager()
        self.logger = gateway.dependency_injector.get_logger()
    
    def initialize(self) -> bool:
        """
        初始化插件
        
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        try:
            self.logger.log("DEBUG", f"初始化插件: {self.__class__.__name__}", None)
            if not self._check_dependencies():
                self.status = self.Status.ERROR
                return False
            self.status = self.Status.RUNNING
            return True
        except Exception as e:
            self.logger.log("ERROR", f"初始化插件时发生错误: {str(e)}", False)
            self.status = self.Status.ERROR
            return False
    
    def shutdown(self) -> bool:
        """
        关闭插件
        
        Returns:
            bool: 关闭成功返回True，失败返回False
        """
        try:
            self.logger.debug(f"关闭插件: {self.__class__.__name__}")
            self.status = self.Status.STOPPED
            return True
        except Exception as e:
            self.logger.error(f"关闭插件时发生错误: {str(e)}")
            return False
    
    def get_name(self) -> str:
        """
        获取插件名称
        
        Returns:
            str: 插件名称
        """
        return self.__class__.__name__
    
    def get_status(self) -> str:
        """
        获取插件状态
        
        Returns:
            str: 插件状态
        """
        return self.status
    
    def _check_dependencies(self) -> bool:
        """
        检查插件依赖
        
        Returns:
            bool: 依赖检查通过返回True，否则返回False
        """
        if not self.dependencies:
            return True
        
        plugin_manager = self.gateway.plugin_manager
        for dep_name in self.dependencies:
            if dep_name not in plugin_manager.plugins:
                self.logger.error(f"插件依赖缺失: {dep_name}")
                return False
            dep_plugin = plugin_manager.plugins[dep_name]
            if dep_plugin.get_status() != self.Status.RUNNING:
                self.logger.error(f"插件依赖未运行: {dep_name}")
                return False
        return True
    
    def reload(self) -> bool:
        """
        重新加载插件
        
        Returns:
            bool: 重新加载成功返回True，失败返回False
        """
        try:
            self.logger.info(f"重新加载插件: {self.__class__.__name__}")
            # 先关闭插件
            self.shutdown()
            # 再初始化插件
            return self.initialize()
        except Exception as e:
            self.logger.error(f"重新加载插件时发生错误: {str(e)}")
            return False
    
    def on_service_reloaded(self, service_id: str) -> None:
        """
        服务重载时的回调方法
        
        Args:
            service_id: 重载的服务ID
        """
        pass
    
    def on_api_mapped(self) -> None:
        """
        API映射完成时的回调方法
        """
        pass
    
    def on_request_incoming(self, request: Any) -> Optional[Any]:
        """
        外部请求进入时的钩子方法
        用途：流量统计、限流、安全检查
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            Optional[Any]: 如果返回响应，则直接返回该响应，阻止后续处理
        """
        pass
    
    def on_service_calling_engine(self, service_id: str, engine_id: str, action: str, data: Dict[str, Any]) -> None:
        """
        服务调用引擎时的钩子方法
        用途：监控调用频率、记录调用链
        
        Args:
            service_id: 源服务ID
            engine_id: 目标引擎ID
            action: 请求动作
            data: 请求数据
        """
        pass
    
    def on_engine_responding(self, engine_id: str, action: str, response: Dict[str, Any]) -> None:
        """
        引擎响应时的钩子方法
        用途：性能监控、错误统计
        
        Args:
            engine_id: 引擎ID
            action: 请求动作
            response: 引擎响应
        """
        pass
    
    def on_route_matching(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """
        路由匹配时的钩子方法
        用途：动态路由、A/B测试、灰度发布
        
        Args:
            path: 请求路径
            method: HTTP方法
            
        Returns:
            Optional[Dict[str, Any]]: 如果返回路由信息，则使用该路由
        """
        pass
    
    def on_response_outgoing(self, response: Any) -> Optional[Any]:
        """
        响应返回给客户端前的钩子方法
        用途：添加响应头、数据脱敏、格式转换
        
        Args:
            response: 响应对象
            
        Returns:
            Optional[Any]: 如果返回响应，则使用该响应
        """
        pass


class PluginManager:
    """
    插件管理器，负责加载和管理所有插件
    """
    
    def __init__(self, gateway):
        """
        初始化插件管理器
        
        Args:
            gateway: LinkGateway实例
        """
        self.gateway = gateway
        self.plugins: Dict[str, Plugin] = {}
        self.logger = get_logger("PluginManager", gateway.path_manager.get_linkgateway_log_path())
        
        # 定义插件目录
        self.plugins_dir = os.path.join(gateway.base_path, "plugins")
        
        # 插件文件修改时间记录
        self.plugin_mod_times = {}
        
        # 注册信息收集结构
        self.registered_plugins = []
        
        # 创建插件目录（如果不存在）
        if not os.path.exists(self.plugins_dir):
            os.makedirs(self.plugins_dir)
    
    def load_plugins(self) -> Dict[str, Any]:
        """
        加载所有插件
        
        Returns:
            Dict[str, Any]: 加载结果，包含成功和失败的插件信息
        """
        self.registered_plugins.clear()
        self.logger.info(f"开始加载插件，插件目录: {self.plugins_dir}")
        
        plugin_files = self._scan_plugin_files(self.plugins_dir)
        result = self._load_plugins_from_files(plugin_files, is_reload=False)
        
        self.logger.info(f"插件加载完成，成功: {len(result['success'])}, 失败: {len(result['failed'])}")
        self._log_registered_plugins()
        
        return result
    
    def reload_plugins(self) -> Dict[str, Any]:
        """
        重新加载所有插件
        
        Returns:
            Dict[str, Any]: 重载结果，包含成功和失败的插件信息
        """
        self.logger.info("开始重新加载插件")
        
        self.shutdown_plugins()
        result = self.load_plugins()
        
        self.logger.info(f"插件重新加载完成，成功: {len(result['success'])}，失败: {len(result['failed'])}")
        return result
    
    def hot_reload_plugins(self) -> Dict[str, Any]:
        """
        热重载插件（只重载修改过的插件）
        
        Returns:
            Dict[str, Any]: 热重载结果，包含成功和失败的插件信息
        """
        self.logger.info("开始热重载插件")
        
        plugin_files = self._scan_plugin_files(self.plugins_dir)
        result = self._hot_reload_plugins_from_files(plugin_files)
        
        self.logger.info(f"插件热重载完成，成功: {len(result['success'])}，失败: {len(result['failed'])}")
        return result
    
    def _scan_plugin_files(self, directory: str) -> List[str]:
        """
        递归扫描插件目录，获取所有插件文件
        
        Args:
            directory: 要扫描的目录
            
        Returns:
            List[str]: 插件文件路径列表
        """
        plugin_files = []
        
        if not os.path.exists(directory):
            return plugin_files
        
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(".py") and not file.startswith("_"):
                    plugin_file = os.path.join(root, file)
                    plugin_files.append(plugin_file)
        
        return plugin_files
    
    def _load_plugins_from_files(self, plugin_files: List[str], is_reload: bool) -> Dict[str, Any]:
        """
        从文件列表加载插件
        
        Args:
            plugin_files: 插件文件路径列表
            is_reload: 是否为重新加载
            
        Returns:
            Dict[str, Any]: 加载结果
        """
        result = {
            "success": [],
            "failed": []
        }
        
        for plugin_file in plugin_files:
            plugin_name = os.path.splitext(os.path.basename(plugin_file))[0]
            load_result = self._load_plugin_from_file(plugin_file, plugin_name, is_reload)
            
            if load_result["success"]:
                result["success"].append(plugin_name)
            else:
                result["failed"].append(plugin_name)
        
        return result
    
    def _hot_reload_plugins_from_files(self, plugin_files: List[str]) -> Dict[str, Any]:
        """
        热重载插件文件（只重载修改过的）
        
        Args:
            plugin_files: 插件文件路径列表
            
        Returns:
            Dict[str, Any]: 热重载结果
        """
        result = {
            "success": [],
            "failed": []
        }
        
        for plugin_file in plugin_files:
            plugin_name = os.path.splitext(os.path.basename(plugin_file))[0]
            current_mod_time = os.path.getmtime(plugin_file)
            
            if plugin_file not in self.plugin_mod_times:
                self.logger.info(f"检测到新插件文件: {plugin_file}")
                load_result = self._load_plugin_from_file(plugin_file, plugin_name, is_reload=False)
            elif current_mod_time != self.plugin_mod_times[plugin_file]:
                self.logger.info(f"检测到插件文件修改: {plugin_file}")
                load_result = self._load_plugin_from_file(plugin_file, plugin_name, is_reload=True)
            else:
                continue
            
            if load_result["success"]:
                result["success"].append(plugin_name)
            else:
                result["failed"].append(plugin_name)
        
        return result
    
    def _log_registered_plugins(self) -> None:
        """
        输出注册成功的插件详情
        """
        if self.registered_plugins:
            self.logger.info("  - 注册成功的插件：")
            for plugin_info in self.registered_plugins:
                plugin_name = plugin_info.get('plugin_name')
                self.logger.info(f"    - 插件{plugin_name} 注册成功 服务ID：{plugin_name}")
    
    def _load_plugin_from_file(self, plugin_file: str, plugin_name: str, is_reload: bool = False) -> Dict[str, Any]:
        """
        从文件加载插件
        
        Args:
            plugin_file: 插件文件路径
            plugin_name: 插件名称
            is_reload: 是否为重新加载
            
        Returns:
            Dict[str, Any]: 加载结果，包含success、failed和plugin_name
        """
        result = {"success": False, "plugin_name": plugin_name}
        
        try:
            plugin = self._import_plugin_class(plugin_file, plugin_name)
            if not plugin:
                return result
            
            self._handle_old_plugin(plugin, is_reload)
            
            if not plugin.initialize():
                self._log_plugin_init_failure(plugin, is_reload)
                return result
            
            self._register_plugin(plugin, plugin_file, is_reload)
            result["success"] = True
        except Exception as e:
            self._log_plugin_load_error(plugin_file, is_reload, e)
        
        return result
    
    def _import_plugin_class(self, plugin_file: str, plugin_name: str) -> Optional[Plugin]:
        """
        从文件导入插件类并创建实例
        
        Args:
            plugin_file: 插件文件路径
            plugin_name: 插件名称
            
        Returns:
            Optional[Plugin]: 插件实例，失败返回None
        """
        spec = importlib.util.spec_from_file_location(plugin_name, plugin_file)
        if not spec or not spec.loader:
            return None
        
        plugin_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(plugin_module)
        
        for name, cls in plugin_module.__dict__.items():
            if isinstance(cls, type) and issubclass(cls, Plugin) and cls != Plugin:
                return cls(self.gateway)
        
        return None
    
    def _handle_old_plugin(self, plugin: Plugin, is_reload: bool) -> None:
        """
        处理旧插件（关闭并删除）
        
        Args:
            plugin: 新插件实例
            is_reload: 是否为重新加载
        """
        if is_reload:
            old_plugin_name = self._find_old_plugin_name(plugin)
            if old_plugin_name:
                old_plugin = self.plugins[old_plugin_name]
                old_plugin.shutdown()
                del self.plugins[old_plugin_name]
        else:
            if plugin.get_name() in self.plugins:
                old_plugin = self.plugins[plugin.get_name()]
                old_plugin.shutdown()
    
    def _find_old_plugin_name(self, plugin: Plugin) -> Optional[str]:
        """
        查找旧插件名称
        
        Args:
            plugin: 新插件实例
            
        Returns:
            Optional[str]: 旧插件名称，未找到返回None
        """
        for p_name, p in self.plugins.items():
            if p.__class__.__name__ == plugin.get_name():
                return p_name
        return None
    
    def _register_plugin(self, plugin: Plugin, plugin_file: str, is_reload: bool) -> None:
        """
        注册插件到管理器
        
        Args:
            plugin: 插件实例
            plugin_file: 插件文件路径
            is_reload: 是否为重新加载
        """
        self.plugins[plugin.get_name()] = plugin
        self.plugin_mod_times[plugin_file] = os.path.getmtime(plugin_file)
        
        plugin_info = {
            'plugin_name': plugin.get_name(),
            'status': plugin.get_status(),
            'path': plugin_file
        }
        self.registered_plugins.append(plugin_info)
        
        if is_reload:
            self.logger.info(f"成功热重载插件: {plugin.get_name()}")
        else:
            self.logger.info(f"加载插件: {plugin.get_name()}")
    
    def _log_plugin_init_failure(self, plugin: Plugin, is_reload: bool) -> None:
        """
        记录插件初始化失败
        
        Args:
            plugin: 插件实例
            is_reload: 是否为重新加载
        """
        if is_reload:
            self.logger.error(f"插件热重载失败: {plugin.get_name()}")
        else:
            self.logger.error(f"插件初始化: {plugin.get_name()}")
    
    def _log_plugin_load_error(self, plugin_file: str, is_reload: bool, error: Exception) -> None:
        """
        记录插件加载错误
        
        Args:
            plugin_file: 插件文件路径
            is_reload: 是否为重新加载
            error: 异常对象
        """
        if is_reload:
            self.logger.error(f"热重载插件失败，文件: {plugin_file}，错误: {str(error)}")
        else:
            self.logger.error(f"加载插件失败，文件: {plugin_file}，错误: {str(error)}")
    
    def get_plugin(self, plugin_name: str) -> Plugin:
        """
        根据名称获取插件实例
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            Plugin: 插件实例，未找到返回None
        """
        return self.plugins.get(plugin_name)
    
    def list_plugins(self) -> List[str]:
        """
        列出所有已加载的插件
        
        Returns:
            List[str]: 插件名称列表
        """
        return list(self.plugins.keys())
    
    def get_plugin_status(self, plugin_name: str) -> str:
        """
        获取插件状态
        
        Args:
            plugin_name: 插件名称
            
        Returns:
            str: 插件状态
        """
        plugin = self.plugins.get(plugin_name)
        if plugin:
            return plugin.get_status()
        return "not_found"
    
    def shutdown_plugins(self) -> None:
        """
        关闭所有插件
        """
        self.logger.info("开始关闭所有插件")
        
        for plugin_name, plugin in self.plugins.items():
            try:
                if plugin.shutdown():
                    self.logger.debug(f"成功关闭插件: {plugin_name}")
                else:
                    self.logger.error(f"关闭插件失败: {plugin_name}")
            except Exception as e:
                self.logger.error(f"关闭插件时发生错误，插件名称: {plugin_name}，错误: {str(e)}")
        
        # 清空插件列表和修改时间记录
        self.plugins.clear()
        self.plugin_mod_times.clear()
        self.logger.info("所有插件已关闭")
    
    def notify_service_reloaded(self, service_id: str) -> None:
        """
        通知所有插件服务已重载
        
        Args:
            service_id: 重载的服务ID
        """
        for plugin in self.plugins.values():
            try:
                plugin.on_service_reloaded(service_id)
            except Exception as e:
                self.logger.error(f"通知插件服务重载时发生错误，插件: {plugin.get_name()}，错误: {str(e)}")
    
    def notify_api_mapped(self) -> None:
        """
        通知所有插件API映射完成
        """
        for plugin in self.plugins.values():
            try:
                plugin.on_api_mapped()
            except Exception as e:
                self.logger.error(f"通知插件API映射完成时发生错误，插件: {plugin.get_name()}，错误: {str(e)}")
    
    def notify_request_incoming(self, request: Any) -> Optional[Any]:
        """
        通知所有插件外部请求进入
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            Optional[Any]: 如果有插件返回响应，则返回该响应
        """
        for plugin in self.plugins.values():
            try:
                response = plugin.on_request_incoming(request)
                if response is not None:
                    return response
            except Exception as e:
                self.logger.error(f"通知插件请求进入时发生错误，插件: {plugin.get_name()}，错误: {str(e)}")
        return None
    
    def notify_service_calling_engine(self, service_id: str, engine_id: str, action: str, data: Dict[str, Any]) -> None:
        """
        通知所有插件服务调用引擎
        
        Args:
            service_id: 源服务ID
            engine_id: 目标引擎ID
            action: 请求动作
            data: 请求数据
        """
        for plugin in self.plugins.values():
            try:
                plugin.on_service_calling_engine(service_id, engine_id, action, data)
            except Exception as e:
                self.logger.error(f"通知插件服务调用引擎时发生错误，插件: {plugin.get_name()}，错误: {str(e)}")
    
    def notify_engine_responding(self, engine_id: str, action: str, response: Dict[str, Any]) -> None:
        """
        通知所有插件引擎响应
        
        Args:
            engine_id: 引擎ID
            action: 请求动作
            response: 引擎响应
        """
        for plugin in self.plugins.values():
            try:
                plugin.on_engine_responding(engine_id, action, response)
            except Exception as e:
                self.logger.error(f"通知插件引擎响应时发生错误，插件: {plugin.get_name()}，错误: {str(e)}")
    
    def notify_route_matching(self, path: str, method: str) -> Optional[Dict[str, Any]]:
        """
        通知所有插件路由匹配
        
        Args:
            path: 请求路径
            method: HTTP方法
            
        Returns:
            Optional[Dict[str, Any]]: 如果有插件返回路由信息，则返回该信息
        """
        for plugin in self.plugins.values():
            try:
                route_info = plugin.on_route_matching(path, method)
                if route_info is not None:
                    return route_info
            except Exception as e:
                self.logger.error(f"通知插件路由匹配时发生错误，插件: {plugin.get_name()}，错误: {str(e)}")
        return None
    
    def notify_response_outgoing(self, response: Any) -> Optional[Any]:
        """
        通知所有插件响应返回
        
        Args:
            response: 响应对象
            
        Returns:
            Optional[Any]: 如果有插件返回响应，则返回该响应
        """
        for plugin in self.plugins.values():
            try:
                plugin_resp = plugin.on_response_outgoing(response)
                if plugin_resp is not None:
                    return plugin_resp
            except Exception as e:
                self.logger.error(f"通知插件响应返回时发生错误，插件: {plugin.get_name()}，错误: {str(e)}")
        return None
