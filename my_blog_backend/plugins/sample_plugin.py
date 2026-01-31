from LinkGateway.plugin import Plugin

class SamplePlugin(Plugin):
    def initialize(self) -> bool:
        """
        初始化插件
        
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        self.logger.info("SamplePlugin 初始化")
        
        # 注册路由
        @self.gateway.app.get("/sample")
        async def sample_endpoint():
            """
            示例插件端点
            """
            return {"message": "Sample plugin endpoint", "plugin": "SamplePlugin"}
        
        return True
    
    def shutdown(self) -> bool:
        """
        关闭插件
        
        Returns:
            bool: 关闭成功返回True，失败返回False
        """
        self.logger.info("SamplePlugin 关闭")
        return True