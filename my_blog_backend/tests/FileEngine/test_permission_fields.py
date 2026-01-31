import unittest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from engines.FileEngine.file_engine import FileEngine


class TestFileEnginePermissionFields(unittest.TestCase):
    """测试FileEngine权限字段功能"""
    
    def setUp(self):
        """设置测试环境"""
        self.engine = FileEngine("FileEngine", "1.0.0")
        self.engine.start()
    
    def tearDown(self):
        """清理测试环境"""
        self.engine.stop()
    
    def test_create_post_with_permission_fields(self):
        """测试创建带权限字段的帖子"""
        create_post = self.engine.handle_request("create_post", {
            "title": "带权限的测试帖子",
            "content": "这是一个带有权限设置的测试帖子内容",
            "permission_level": "p1",
            "created_by": "test_user_123",
            "is_public": False
        })
        
        self.assertEqual(create_post["status"], "success")
        self.assertIn("post_id", create_post)
        
        # 清理测试数据
        if create_post["status"] == "success":
            self.engine.handle_request("delete_post", {"post_id": create_post["post_id"]})
    
    def test_get_post_with_permission_fields(self):
        """测试获取带权限字段的帖子"""
        create_post = self.engine.handle_request("create_post", {
            "title": "带权限的测试帖子",
            "content": "这是一个带有权限设置的测试帖子内容",
            "permission_level": "p1",
            "created_by": "test_user_123",
            "is_public": False
        })
        
        if create_post["status"] == "success":
            post_id = create_post["post_id"]
            get_post = self.engine.handle_request("get_post", {"post_id": post_id})
            
            self.assertEqual(get_post["status"], "success")
            
            # 清理测试数据
            self.engine.handle_request("delete_post", {"post_id": post_id})
    
    def test_update_post_permission_fields(self):
        """测试更新帖子权限字段"""
        create_post = self.engine.handle_request("create_post", {
            "title": "带权限的测试帖子",
            "content": "这是一个带有权限设置的测试帖子内容",
            "permission_level": "p1",
            "created_by": "test_user_123",
            "is_public": False
        })
        
        if create_post["status"] == "success":
            post_id = create_post["post_id"]
            
            update_post = self.engine.handle_request("update_post", {
                "post_id": post_id,
                "permission_level": "p2",
                "is_public": True
            })
            
            self.assertEqual(update_post["status"], "success")
            
            # 清理测试数据
            self.engine.handle_request("delete_post", {"post_id": post_id})
    
    def test_create_post_with_default_permission(self):
        """测试创建默认权限字段的帖子"""
        create_post = self.engine.handle_request("create_post", {
            "title": "默认权限的测试帖子",
            "content": "这是一个使用默认权限设置的测试帖子内容"
        })
        
        self.assertEqual(create_post["status"], "success")
        self.assertIn("post_id", create_post)
        
        # 清理测试数据
        if create_post["status"] == "success":
            self.engine.handle_request("delete_post", {"post_id": create_post["post_id"]})


if __name__ == "__main__":
    unittest.main()
