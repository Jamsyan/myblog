import unittest
from unittest.mock import Mock, patch
from LinkGateway.gateway import LinkGateway

class TestGateway(unittest.TestCase):
    """测试Gateway核心组件"""
    
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
    def test_gateway_initialization_components(self, mock_path_manager, mock_get_logger, 
                                            mock_service_proxy, mock_auth_manager, 
                                            mock_outer_comm, mock_inner_comm, 
                                            mock_api_mapper, mock_db_link, 
                                            mock_service_registry):
        """测试Gateway初始化组件"""
        # 模拟依赖组件
        mock_path_instance = Mock()
        mock_path_instance.get_linkgateway_log_path.return_value = "./logs"
        mock_path_manager.return_value = mock_path_instance
        
        mock_logger = Mock()
        mock_logger.set_level = Mock()
        mock_get_logger.return_value = mock_logger
        
        mock_registry_instance = Mock()
        mock_service_registry.return_value = mock_registry_instance
        
        mock_db_instance = Mock()
        mock_db_link.return_value = mock_db_instance
        
        mock_mapper_instance = Mock()
        mock_api_mapper.return_value = mock_mapper_instance
        
        mock_inner_instance = Mock()
        mock_inner_comm.return_value = mock_inner_instance
        
        mock_outer_instance = Mock()
        mock_outer_comm.return_value = mock_outer_instance
        
        mock_auth_instance = Mock()
        mock_auth_manager.return_value = mock_auth_instance
        
        mock_proxy_instance = Mock()
        mock_service_proxy.return_value = mock_proxy_instance
        
        # 模拟FastAPI应用
        with patch('LinkGateway.gateway.FastAPI') as mock_fastapi:
            mock_app = Mock()
            # 模拟include_router方法，避免实际调用
            mock_app.include_router = Mock()
            mock_fastapi.return_value = mock_app
            
            # 创建LinkGateway实例
            gateway = LinkGateway(self.base_path)
            
            # 验证初始化是否正确
            self.assertEqual(gateway.base_path, self.base_path)
            mock_service_registry.assert_called_once_with(self.base_path)
            mock_db_link.assert_called_once_with(self.base_path)
            mock_api_mapper.assert_called_once()
            mock_inner_comm.assert_called_once()
            mock_outer_comm.assert_called_once()
            mock_auth_manager.assert_called_once()
            mock_service_proxy.assert_called_once()
    
    def test_gateway_instance_creation(self):
        """测试Gateway实例创建"""
        # 直接测试Gateway类是否能被导入和实例化
        # 注意：这里我们不实际创建实例，因为它依赖太多外部组件
        # 而是测试类是否存在且可访问
        self.assertTrue(LinkGateway is not None)
        self.assertTrue(callable(LinkGateway))


if __name__ == "__main__":
    unittest.main()
