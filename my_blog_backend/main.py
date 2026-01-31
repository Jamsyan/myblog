import os
import sys
import traceback
import signal
import atexit
from LinkGateway import LinkGateway

# 获取项目根目录路径
base_path = os.path.dirname(os.path.abspath(__file__))

# 全局变量，用于存储gateway实例
gateway_instance = None

def cleanup_resources():
    """
    清理资源的函数，在程序退出时调用
    """
    global gateway_instance
    if not gateway_instance:
        return
    
    try:
        gateway_instance.shutdown()
    except Exception:
        pass

def signal_handler(signum, frame):
    """
    信号处理器，用于优雅关闭
    """
    global gateway_instance
    cleanup_resources()
    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# 注册退出时的清理函数
atexit.register(cleanup_resources)

try:
    # 创建LinkGateway实例
    gateway = LinkGateway(base_path, debug=False)
    gateway_instance = gateway
    
    # 暴露FastAPI应用实例，供uvicorn直接调用
    app = gateway.get_app()

    def main():
        """
        应用入口函数
        """
        try:
            gateway.start(host="0.0.0.0", port=8000)
        except KeyboardInterrupt:
            cleanup_resources()
            sys.exit(0)
        except Exception as e:
            traceback.print_exc()
            cleanup_resources()
            sys.exit(1)

if __name__ == "__main__":
    main()
except Exception as e:
    traceback.print_exc()
    cleanup_resources()
    sys.exit(1)
