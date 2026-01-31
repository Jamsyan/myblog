from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import sys
import os

# 添加当前目录到sys.path，确保动态导入时能找到模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 使用LinkGateway提供的日志模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from LinkGateway.logs import get_logger
logger = get_logger("interaction-service")

# 导入核心业务逻辑
from core import InteractionService

# 创建API路由器
router = APIRouter()

# 获取项目根目录
current_path = os.path.abspath(__file__)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))

# 服务数据目录
os.makedirs(os.path.join(project_root, "data", "services", "interaction-service"), exist_ok=True)

# 数据库路径 - 使用user-server服务的数据库
# 这里使用与user-server相同的数据库文件，因为我们需要共享Asset表
user_server_db_path = os.path.join(project_root, "data", "services", "user-server", "user-server.db")

# 确保数据库目录存在
os.makedirs(os.path.dirname(user_server_db_path), exist_ok=True)

# 直接创建InteractionService实例，不通过从database导入
interaction_service = InteractionService(db_path=user_server_db_path)

# 获取数据库会话的依赖项
def get_db():
    """
    获取数据库会话
    
    Returns:
        Session: 数据库会话实例
    """
    # 动态导入InteractionDatabase，避免模块导入冲突
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from database import InteractionDatabase
    
    db_instance = InteractionDatabase(user_server_db_path)
    db_gen = db_instance.get_db()
    db = next(db_gen)
    try:
        yield db
    finally:
        db.close()

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

# 点赞帖子
@router.post("/posts/{post_id}/like", response_model=Dict[str, Any], status_code=201)
async def like_post(
    post_id: str,
    like_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    点赞帖子
    
    请求体参数：
    - user_id: 用户ID（必填）
    """
    # 验证必填字段
    if "user_id" not in like_data:
        raise HTTPException(status_code=400, detail={"error": "Missing required field: user_id"})
    
    user_id = like_data["user_id"]
    
    # 调用互动服务点赞帖子
    result = interaction_service.like_post(db, user_id, post_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
    
    return result

# 取消点赞
@router.delete("/posts/{post_id}/like", response_model=Dict[str, Any])
async def unlike_post(
    post_id: str,
    unlike_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    取消点赞
    
    请求体参数：
    - user_id: 用户ID（必填）
    """
    # 验证必填字段
    if "user_id" not in unlike_data:
        raise HTTPException(status_code=400, detail={"error": "Missing required field: user_id"})
    
    user_id = unlike_data["user_id"]
    
    # 调用互动服务取消点赞
    result = interaction_service.unlike_post(db, user_id, post_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
    
    return result

# 获取帖子点赞数
@router.get("/posts/{post_id}/likes", response_model=Dict[str, Any])
async def get_post_likes(
    post_id: str,
    db: Session = Depends(get_db)
):
    """
    获取帖子点赞数
    """
    # 调用互动服务获取点赞数
    result = interaction_service.get_post_likes(db, post_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
    
    return result

# 获取用户点赞记录
@router.get("/users/{user_id}/likes", response_model=Dict[str, Any])
async def get_user_likes(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取用户点赞记录
    
    查询参数：
    - skip: 跳过的记录数（可选，默认值为0）
    - limit: 返回的记录数（可选，默认值为100）
    """
    # 调用互动服务获取用户点赞记录
    result = interaction_service.get_user_likes(db, user_id, skip, limit)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
    
    return result

# 添加评论
@router.post("/posts/{post_id}/comments", response_model=Dict[str, Any], status_code=201)
async def add_comment(
    post_id: str,
    comment_data: Dict[str, Any]
):
    """
    添加评论
    
    请求体参数：
    - content: 评论内容（必填）
    - author: 评论作者（必填）
    """
    # 验证必填字段
    required_fields = ["content", "author"]
    for field in required_fields:
        if field not in comment_data:
            raise HTTPException(status_code=400, detail={"error": f"Missing required field: {field}"})
    
    # 调用互动服务添加评论
    result = interaction_service.add_comment(post_id, comment_data)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
    
    return result

# 获取帖子评论
@router.get("/posts/{post_id}/comments", response_model=Dict[str, Any])
async def get_comments(
    post_id: str,
    page: int = 1,
    limit: int = 20
):
    """
    获取帖子评论
    
    查询参数：
    - page: 页码（可选，默认值为1）
    - limit: 每页数量（可选，默认值为20）
    """
    # 调用互动服务获取评论
    result = interaction_service.get_comments(post_id, page, limit)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
    
    return result

# 删除评论
@router.delete("/comments/{comment_id}", response_model=Dict[str, Any])
async def delete_comment(
    comment_id: str
):
    """
    删除评论
    """
    # 调用互动服务删除评论
    result = interaction_service.delete_comment(comment_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result)
    
    return result