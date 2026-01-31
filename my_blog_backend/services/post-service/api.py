from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import sys
import os
import importlib.util

# 使用LinkGateway提供的日志模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from LinkGateway.logs import get_logger
logger = get_logger("post-service")

# 获取core模块的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
core_path = os.path.join(current_dir, "core.py")

# 使用绝对路径创建模块规范
spec = importlib.util.spec_from_file_location('core', core_path)
if spec and spec.loader:
    # 创建模块并执行
    core_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(core_module)
    PostService = core_module.PostService
else:
    raise ImportError(f"Failed to import core module from {core_path}")

# 创建API路由器
router = APIRouter()



# 获取项目根目录
current_path = os.path.abspath(__file__)
# 向上遍历，找到项目根目录（包含main.py的目录）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))

# 服务数据目录 - 使用项目根目录下的data/services文件夹
service_data_dir = os.path.join(project_root, "data", "services", "post-service")
# 确保数据目录存在
os.makedirs(service_data_dir, exist_ok=True)

# 数据库路径 - 使用user-server服务的数据库，因为根据开发指南，我们需要统一使用用户服务已提供的数据库资源
db_path = os.path.join(project_root, "data", "services", "user-server", "user-server.db")

# 创建PostService实例（暂时保留直接创建方式，后续会通过db_link注入）
post_service = PostService(db_path)


# 设置路由的函数，会被API映射器调用
def setup_router(app, apis=None, db_link=None):
    """
    设置路由，将路由器挂载到FastAPI应用
    
    Args:
        app: FastAPI应用实例或APIRouter实例
        apis: API定义列表（可选）
        db_link: DatabaseLinkManager实例（可选）
    """
    app.include_router(router)


# 创建帖子
@router.post("/posts", response_model=Dict[str, Any], status_code=201)
async def create_post(
    post_data: Dict[str, Any]
):
    """
    创建帖子
    
    请求体参数：
    - user_id: 用户ID（必填）
    - title: 帖子标题（必填）
    - content: 帖子内容（必填）
    - permission_level: 帖子权限等级（可选，默认值为"P3"）
    """
    # 验证必填字段
    required_fields = ["user_id", "title", "content"]
    for field in required_fields:
        if field not in post_data:
            raise HTTPException(status_code=400, detail={"error": f"Missing required field: {field}"})
    
    # 调用PostService创建帖子
    result = post_service.create_post(
        user_id=post_data["user_id"],
        title=post_data["title"],
        content=post_data["content"],
        permission_level=post_data.get("permission_level", "P3")
    )
    
    if "error" in result:
        raise HTTPException(status_code=403 if "无权限" in result["error"] else 400, detail=result)
    
    return result


# 获取帖子列表
@router.get("/posts", response_model=Dict[str, Any])
async def get_posts(
    user_id: int,
    page: int = 1,
    limit: int = 10
):
    """
    获取帖子列表（带权限过滤）
    
    查询参数：
    - user_id: 用户ID（必填）
    - page: 页码（可选，默认值为1）
    - limit: 每页数量（可选，默认值为10）
    """
    # 调用PostService获取帖子列表
    result = post_service.get_posts(user_id, page, limit)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result)
    
    return result


# 获取单个帖子
@router.get("/posts/{post_id}", response_model=Dict[str, Any])
async def get_post(
    post_id: str,
    user_id: int
):
    """
    获取单个帖子（带权限验证）
    
    查询参数：
    - user_id: 用户ID（必填）
    """
    # 调用PostService获取帖子
    result = post_service.get_post(post_id, user_id)
    
    if "error" in result:
        raise HTTPException(status_code=403 if "无权限" in result["error"] else 404, detail=result)
    
    return result


# 更新帖子
@router.put("/posts/{post_id}", response_model=Dict[str, Any])
async def update_post(
    post_id: str,
    post_data: Dict[str, Any]
):
    """
    更新帖子
    
    请求体参数：
    - user_id: 用户ID（必填）
    - title: 帖子标题（可选）
    - content: 帖子内容（可选）
    - permission_level: 帖子权限等级（可选）
    """
    # 验证必填字段
    if "user_id" not in post_data:
        raise HTTPException(status_code=400, detail={"error": "Missing required field: user_id"})
    
    # 调用PostService更新帖子
    result = post_service.update_post(
        post_id=post_id,
        user_id=post_data["user_id"],
        title=post_data.get("title"),
        content=post_data.get("content"),
        permission_level=post_data.get("permission_level")
    )
    
    if "error" in result:
        raise HTTPException(status_code=403 if "无权限" in result["error"] else 404, detail=result)
    
    return result


# 删除帖子
@router.delete("/posts/{post_id}", response_model=Dict[str, Any])
async def delete_post(
    post_id: str,
    post_data: Dict[str, Any]
):
    """
    删除帖子
    
    请求体参数：
    - user_id: 用户ID（必填）
    """
    # 验证必填字段
    if "user_id" not in post_data:
        raise HTTPException(status_code=400, detail={"error": "Missing required field: user_id"})
    
    # 调用PostService删除帖子
    result = post_service.delete_post(post_id, post_data["user_id"])
    
    if "error" in result:
        raise HTTPException(status_code=403 if "无权限" in result["error"] else 404, detail=result)
    
    return result
