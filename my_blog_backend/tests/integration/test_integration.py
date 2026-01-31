import unittest
from unittest.mock import Mock, patch

class TestIntegration(unittest.TestCase):
    """测试组件间集成"""
    
    def setUp(self):
        """设置测试环境"""
        self.base_path = "."
    
    @patch('LinkGateway.gateway.ServiceRegistry')
    @patch('LinkGateway.gateway.DatabaseLinkManager')
    @patch('LinkGateway.gateway.APIMapper')
    @patch('LinkGateway.gateway.InnerCommunicator')
    @patch('LinkGateway.gateway.OuterCommunicator')
    @patch('LinkGateway.gateway.AuthManager')
    @patch('LinkGateway.gateway.ServiceProxy')
    @patch('LinkGateway.gateway.get_logger')
    @patch('LinkGateway.gateway.PathManager')
    def test_gateway_components_integration(self, mock_path_manager, mock_get_logger, 
                                          mock_service_proxy, mock_auth_manager, 
                                          mock_outer_comm, mock_inner_comm, 
                                          mock_api_mapper, mock_db_link, 
                                          mock_service_registry):
        """测试Gateway组件间的集成"""
        # 模拟依赖组件
        mock_path_instance = Mock()
        mock_path_instance.get_linkgateway_log_path.return_value = "./logs"
        mock_path_manager.return_value = mock_path_instance
        
        mock_logger = Mock()
        mock_logger.set_level = Mock()
        mock_logger.info = Mock()
        mock_logger.error = Mock()
        mock_get_logger.return_value = mock_logger
        
        # 模拟ServiceRegistry
        mock_registry_instance = Mock()
        mock_registry_instance.discover_services.return_value = {"total_services": 0}
        mock_service_registry.return_value = mock_registry_instance
        
        # 模拟DatabaseLinkManager
        mock_db_instance = Mock()
        mock_db_link.return_value = mock_db_instance
        
        # 模拟APIMapper
        mock_mapper_instance = Mock()
        mock_mapper_instance.add_route = Mock(return_value=True)
        mock_mapper_instance.get_route = Mock(return_value=None)
        mock_api_mapper.return_value = mock_mapper_instance
        
        # 模拟其他组件
        mock_inner_instance = Mock()
        mock_inner_comm.return_value = mock_inner_instance
        
        mock_outer_instance = Mock()
        mock_outer_comm.return_value = mock_outer_instance
        
        mock_auth_instance = Mock()
        mock_auth_manager.return_value = mock_auth_instance
        
        mock_proxy_instance = Mock()
        mock_proxy_instance.get_proxy_router = Mock(return_value=Mock(routes=[]))
        mock_proxy_instance.stop = Mock(return_value=True)
        mock_service_proxy.return_value = mock_proxy_instance
        
        # 模拟FastAPI应用
        with patch('LinkGateway.gateway.FastAPI') as mock_fastapi, \
             patch('uvicorn.run') as mock_uvicorn_run, \
             patch('threading.Thread') as mock_thread:
            mock_app = Mock()
            mock_app.include_router = Mock()
            mock_fastapi.return_value = mock_app
            
            # 模拟uvicorn.run已经在外部完成
            
            # 模拟线程
            mock_thread_instance = Mock()
            mock_thread.return_value = mock_thread_instance
            mock_thread_instance.daemon = True
            mock_thread_instance.start = Mock()
            
            # 导入LinkGateway（在模拟后导入）
            from LinkGateway.gateway import LinkGateway
            
            # 创建LinkGateway实例
            gateway = LinkGateway(self.base_path)
            
            # 测试Gateway启动
            gateway.start()
            # start方法返回None，所以不检查返回值
            # 验证服务发现是否被调用
            mock_registry_instance.discover_services.assert_called_once()
            
            # 测试Gateway初始化和启动完成
            # LinkGateway类没有stop方法，所以只测试启动过程
            self.assertIsNotNone(gateway)
            mock_registry_instance.discover_services.assert_called_once()
    
    @patch('LinkGateway.registry.get_logger')
    @patch('BaseEngine.engine_registry.EngineRegistry')
    @patch('threading.Thread')
    def test_registry_discovery_integration(self, mock_thread, mock_engine_registry, mock_get_logger):
        """测试ServiceRegistry的服务发现集成"""
        # 模拟依赖
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_engine_registry_instance = Mock()
        mock_engine_registry.return_value = mock_engine_registry_instance
        
        # 模拟线程
        mock_thread_instance = Mock()
        mock_thread.return_value = mock_thread_instance
        mock_thread_instance.daemon = True
        mock_thread_instance.start = Mock()
        
        # 导入ServiceRegistry（在模拟后导入）
        from LinkGateway.registry import ServiceRegistry
        
        # 创建ServiceRegistry实例
        registry = ServiceRegistry(self.base_path)
        
        # 测试服务注册表的初始化
        self.assertIsNotNone(registry)
        
        # 测试服务发现
        result = registry.discover_services()
        self.assertIsInstance(result, dict)
        self.assertIn("businesses", result)
        self.assertIn("engines", result)
        self.assertIn("total_services", result)
    
    def test_api_mapper_routing_integration(self):
        """测试APIMapper的路由映射集成"""
        # 导入APIMapper
        from LinkGateway.api_mapper import APIMapper
        
        # 创建APIMapper实例
        api_mapper = APIMapper()
        
        # 测试添加路由（使用正确的方法签名）
        service_id = "test-service"
        path = "/test"
        endpoint = lambda: "test"
        
        # 添加GET路由
        result = api_mapper.add_api_route(service_id, path, endpoint, methods=["GET"])
        self.assertTrue(result)
        
        # 测试添加POST路由
        post_endpoint = lambda: "test post"
        result = api_mapper.add_api_route(service_id, "/test", post_endpoint, methods=["POST"])
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
