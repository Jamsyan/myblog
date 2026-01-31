import os
import sys
from LinkGateway import LinkGateway

# 获取项目根目录路径
base_path = os.path.dirname(os.path.abspath(__file__))

print("=== 测试LinkGateway日志输出效果 ===")
print("创建LinkGateway实例...")

# 创建LinkGateway实例（debug=False，只看INFO级别日志）
gateway = LinkGateway(base_path, debug=False)

print("\n=== 开始测试服务发现 ===")
print("注意：在debug=False模式下，应该只看到INFO级别的汇总日志，")
print("不应该看到详细的单个服务/引擎注册日志。")
print("\n开始服务发现...")

# 执行服务发现
try:
    result = gateway.discover_services()
    print("\n服务发现完成！")
    print(f"发现的服务总数: {result.get('total_services', 0)}")
    
    # 打印服务发现结果
    businesses = result.get('businesses', [])
    engines = result.get('engines', [])
    
    print(f"\n业务服务: {len(businesses)} 个")
    for business in businesses:
        print(f"  - {business.get('service_id')}: {business.get('status')}")
    
    print(f"\n引擎服务: {len(engines)} 个")
    for engine in engines:
        print(f"  - {engine.get('service_id')}: {engine.get('status')}")
    
    print("\n=== 测试完成 ===")
    print("检查日志文件，确认:")
    print("1. INFO级别日志是否只包含汇总信息")
    print("2. DEBUG级别日志是否包含详细信息")
    print("3. 日志输出是否简洁明了")
    
except Exception as e:
    print(f"测试过程中发生错误: {e}")
    import traceback
    traceback.print_exc()

print("\n测试脚本执行完毕！")
