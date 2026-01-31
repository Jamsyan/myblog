import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class AuthManager:
    """
    身份认证与授权类，负责管理服务身份标识和认证机制
    """
    
    def __init__(self, secret_key: str = None):
        """
        初始化认证管理器
        
        Args:
            secret_key: 用于签名和验证的密钥，默认为随机生成
        """
        self.secret_key = secret_key or str(uuid.uuid4())
        self.service_tokens: Dict[str, Dict[str, Any]] = {}
        self.api_keys: Dict[str, Dict[str, Any]] = {}
    
    def generate_service_id(self, service_name: str) -> str:
        """
        生成服务ID
        
        Args:
            service_name: 服务名称
            
        Returns:
            str: 生成的服务ID
        """
        # 使用服务名称和当前时间生成唯一ID
        unique_str = f"{service_name}_{datetime.utcnow().isoformat()}"
        service_id = hashlib.md5(unique_str.encode()).hexdigest()
        return service_id
    
    def generate_api_key(self, service_id: str, expires_in: int = 3600 * 24 * 30) -> str:
        """
        生成API密钥
        
        Args:
            service_id: 服务ID
            expires_in: 过期时间，单位为秒，默认为30天
            
        Returns:
            str: 生成的API密钥
        """
        # 生成随机密钥
        api_key = str(uuid.uuid4())
        
        # 计算过期时间
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
        
        # 存储API密钥信息
        self.api_keys[api_key] = {
            "service_id": service_id,
            "expires_at": expires_at,
            "created_at": datetime.utcnow()
        }
        
        return api_key
    
    def verify_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        验证API密钥
        
        Args:
            api_key: API密钥
            
        Returns:
            Optional[Dict[str, Any]]: 验证成功返回密钥信息，失败返回None
        """
        # 检查API密钥是否存在
        if api_key not in self.api_keys:
            return None
        
        key_info = self.api_keys[api_key]
        
        # 检查API密钥是否过期
        if datetime.utcnow() > key_info["expires_at"]:
            # 移除过期密钥
            del self.api_keys[api_key]
            return None
        
        return key_info
    
    def generate_service_token(self, service_id: str) -> str:
        """
        生成服务令牌，用于服务间通信
        
        Args:
            service_id: 服务ID
            
        Returns:
            str: 生成的服务令牌
        """
        # 生成服务令牌
        token = str(uuid.uuid4())
        
        # 存储服务令牌信息
        self.service_tokens[token] = {
            "service_id": service_id,
            "created_at": datetime.utcnow()
        }
        
        return token
    
    def verify_service_token(self, token: str) -> Optional[str]:
        """
        验证服务令牌
        
        Args:
            token: 服务令牌
            
        Returns:
            Optional[str]: 验证成功返回服务ID，失败返回None
        """
        # 检查服务令牌是否存在
        if token not in self.service_tokens:
            return None
        
        token_info = self.service_tokens[token]
        return token_info["service_id"]
    
    def sign_request(self, request_data: Dict[str, Any]) -> str:
        """
        签名请求数据
        
        Args:
            request_data: 请求数据
            
        Returns:
            str: 签名结果
        """
        # 将请求数据转换为字符串
        data_str = str(request_data)
        
        # 使用HMAC-SHA256生成签名
        signature = hmac.new(
            self.secret_key.encode(),
            data_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def verify_signature(self, request_data: Dict[str, Any], signature: str) -> bool:
        """
        验证请求签名
        
        Args:
            request_data: 请求数据
            signature: 签名结果
            
        Returns:
            bool: 验证成功返回True，失败返回False
        """
        # 生成签名
        expected_signature = self.sign_request(request_data)
        
        # 比较签名
        return hmac.compare_digest(expected_signature, signature)
    
    def create_service_identity(self, service_name: str, service_type: str) -> Dict[str, Any]:
        """
        创建服务身份标识
        
        Args:
            service_name: 服务名称
            service_type: 服务类型
            
        Returns:
            Dict[str, Any]: 服务身份标识信息
        """
        # 生成服务ID
        service_id = self.generate_service_id(service_name)
        
        # 生成API密钥
        api_key = self.generate_api_key(service_id)
        
        # 生成服务令牌
        service_token = self.generate_service_token(service_id)
        
        return {
            "service_id": service_id,
            "service_name": service_name,
            "service_type": service_type,
            "api_key": api_key,
            "service_token": service_token
        }
    
    def check_permission(self, service_id: str, action: str) -> bool:
        """
        检查服务权限
        
        Args:
            service_id: 服务ID
            action: 请求动作
            
        Returns:
            bool: 有权限返回True，无权限返回False
        """
        # 这里可以添加权限检查逻辑
        # 例如，检查服务是否有权限执行特定动作
        # 目前默认所有服务都有权限
        return True
    
    def revoke_api_key(self, api_key: str) -> bool:
        """
        撤销API密钥
        
        Args:
            api_key: API密钥
            
        Returns:
            bool: 撤销成功返回True，失败返回False
        """
        if api_key in self.api_keys:
            del self.api_keys[api_key]
            return True
        return False
    
    def revoke_service_token(self, token: str) -> bool:
        """
        撤销服务令牌
        
        Args:
            token: 服务令牌
            
        Returns:
            bool: 撤销成功返回True，失败返回False
        """
        if token in self.service_tokens:
            del self.service_tokens[token]
            return True
        return False
    
    def get_service_info_by_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        通过API密钥获取服务信息
        
        Args:
            api_key: API密钥
            
        Returns:
            Optional[Dict[str, Any]]: 服务信息，未找到返回None
        """
        key_info = self.verify_api_key(api_key)
        if key_info:
            return {
                "service_id": key_info["service_id"]
            }
        return None
