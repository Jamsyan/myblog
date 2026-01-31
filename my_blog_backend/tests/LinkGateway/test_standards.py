import unittest
from LinkGateway.standards import ServiceStandard, EngineStandard, APIStandard

class TestServiceStandard(unittest.TestCase):
    """测试服务标准验证"""
    
    def test_validate_service_json_valid(self):
        """测试验证有效的服务配置文件"""
        valid_service_json = {
            "service_id": "test-service",
            "service_name": "测试服务",
            "version": "1.0.0",
            "description": "测试服务描述",
            "apis": [
                {
                    "path": "/test",
                    "method": "GET",
                    "description": "测试接口"
                }
            ],
            "database": {
                "type": "sqlite",
                "name": "test-db"
            }
        }
        result = ServiceStandard.validate_service_json(valid_service_json)
        self.assertTrue(result["valid"])
    
    def test_validate_service_json_missing_required_fields(self):
        """测试验证缺少必填字段的服务配置文件"""
        invalid_service_json = {
            "service_name": "测试服务",
            "version": "1.0.0"
        }
        result = ServiceStandard.validate_service_json(invalid_service_json)
        self.assertFalse(result["valid"])
        self.assertIn("Missing required field", result["reason"])
    
    def test_validate_service_json_invalid_database_type(self):
        """测试验证无效数据库类型的服务配置文件"""
        invalid_service_json = {
            "service_id": "test-service",
            "service_name": "测试服务",
            "version": "1.0.0",
            "database": {
                "type": "invalid-type"
            }
        }
        result = ServiceStandard.validate_service_json(invalid_service_json)
        self.assertFalse(result["valid"])
        self.assertIn("Unsupported database type", result["reason"])

class TestEngineStandard(unittest.TestCase):
    """测试引擎标准验证"""
    
    def test_validate_engine_json_valid(self):
        """测试验证有效的引擎配置文件"""
        valid_engine_json = {
            "service_id": "test-engine",
            "service_name": "测试引擎",
            "version": "1.0.0",
            "engine_type": "kernel",
            "description": "测试引擎描述",
            "apis": [
                {
                    "path": "/health",
                    "method": "GET",
                    "description": "健康检查接口"
                }
            ]
        }
        result = EngineStandard.validate_engine_json(valid_engine_json)
        self.assertTrue(result["valid"])
    
    def test_validate_engine_json_invalid_engine_type(self):
        """测试验证无效引擎类型的引擎配置文件"""
        invalid_engine_json = {
            "service_id": "test-engine",
            "service_name": "测试引擎",
            "version": "1.0.0",
            "engine_type": "invalid-type"
        }
        result = EngineStandard.validate_engine_json(invalid_engine_json)
        self.assertFalse(result["valid"])
        self.assertIn("Invalid engine type", result["reason"])

class TestAPIStandard(unittest.TestCase):
    """测试API标准验证"""
    
    def test_format_api_path_service(self):
        """测试格式化服务API路径"""
        path = APIStandard.format_api_path("business", "test-service", "/test")
        self.assertEqual(path, "/api/test-service/test")
    
    def test_format_api_path_engine(self):
        """测试格式化引擎API路径"""
        path = APIStandard.format_api_path("engine", "test-engine", "/health")
        self.assertEqual(path, "/api/test-engine/health")
    
    def test_format_api_path_already_formatted(self):
        """测试格式化已经格式化的API路径"""
        path = APIStandard.format_api_path("business", "test-service", "/api/test-service/test")
        self.assertEqual(path, "/api/test-service/test")
    
    def test_validate_api_method_supported(self):
        """测试验证支持的HTTP方法"""
        self.assertTrue(APIStandard.validate_api_method("GET"))
        self.assertTrue(APIStandard.validate_api_method("POST"))
        self.assertTrue(APIStandard.validate_api_method("PUT"))
        self.assertTrue(APIStandard.validate_api_method("DELETE"))
    
    def test_validate_api_method_unsupported(self):
        """测试验证不支持的HTTP方法"""
        self.assertFalse(APIStandard.validate_api_method("INVALID"))
    
    def test_normalize_api_method(self):
        """测试标准化HTTP方法"""
        self.assertEqual(APIStandard.normalize_api_method("get"), "GET")
        self.assertEqual(APIStandard.normalize_api_method("post"), "POST")
        self.assertEqual(APIStandard.normalize_api_method("PUT"), "PUT")

if __name__ == "__main__":
    unittest.main()
