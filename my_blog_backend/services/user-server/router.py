from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
import sys
import os

# 添加当前目录到sys.path，确保动态导入时能找到模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from service import UserServerService


# 创建API路由器
router = APIRouter()


# 导入数据库相关模块
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# 获取项目根目录
current_path = os.path.abspath(__file__)
# 向上遍历，找到项目根目录（包含main.py的目录）
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))

# 服务数据目录 - 使用项目根目录下的data/services文件夹
service_data_dir = os.path.join(project_root, "data", "services", "user-server")
# 确保数据目录存在
os.makedirs(service_data_dir, exist_ok=True)

# 创建SQLite数据库引擎
db_path = os.path.join(service_data_dir, "user-server.db")
engine = create_engine(f"sqlite:///{db_path}")

# 创建SessionLocal类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 导入模型
from models import Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 数据库依赖
def get_db():
    """
    获取数据库会话的依赖函数
    """
    db = SessionLocal()
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
        apis: API定义（可选）
        db_link: DatabaseLinkManager实例（可选）
    """
    # 将路由器挂载到传入的app
    app.include_router(router)


# 用户注册
@router.post("/register", response_model=Dict[str, Any], status_code=201)
async def register_user(
    user_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    请求体参数：
    - username: 用户名（必填）
    - email: 邮箱（必填）
    - password: 密码（必填）
    - full_name: 完整名称（可选）
    """
    user_server = UserServerService(db)
    
    # 验证必填字段
    required_fields = ["username", "email", "password"]
    for field in required_fields:
        if field not in user_data:
            raise HTTPException(status_code=400, detail={"error": f"Missing required field: {field}"})
    
    # 创建用户
    user = user_server.create_user(user_data)
    if not user:
        raise HTTPException(status_code=400, detail={"error": "Failed to create user, username or email may already exist"})
    
    # 返回创建的用户信息
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "permission_level": user.permission_level,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat()
    }


# 用户登录
@router.post("/login", response_model=Dict[str, Any])
async def login_user(
    login_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    请求体参数：
    - username: 用户名（必填）
    - password: 密码（必填）
    """
    user_server = UserServerService(db)
    
    # 验证必填字段
    if "username" not in login_data or "password" not in login_data:
        raise HTTPException(status_code=400, detail={"error": "Missing username or password"})
    
    # 验证用户
    user = user_server.authenticate_user(login_data["username"], login_data["password"])
    if not user:
        raise HTTPException(status_code=401, detail={"error": "Invalid username or password"})
    
    # 返回登录成功信息和用户权限
    return {
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "permission_level": user.permission_level
        },
        "permissions": user.permission_list
    }


# 获取用户信息
@router.get("/users/{user_id}", response_model=Dict[str, Any])
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户信息
    """
    user_server = UserServerService(db)
    user = user_server.get_user(user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "permission_level": user.permission_level,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat()
    }


# 更新用户信息
@router.put("/users/{user_id}", response_model=Dict[str, Any])
async def update_user(
    user_id: int,
    user_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    """
    user_server = UserServerService(db)
    user = user_server.update_user(user_id, user_data)
    
    if not user:
        raise HTTPException(status_code=404, detail={"error": "User not found"})
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "permission_level": user.permission_level,
        "is_active": user.is_active,
        "updated_at": user.updated_at.isoformat()
    }


# 获取用户权限
@router.get("/users/{user_id}/permissions", response_model=Dict[str, Any])
async def get_user_permissions(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户权限
    """
    user_server = UserServerService(db)
    permissions = user_server.get_user_permissions(user_id)
    
    if "error" in permissions:
        raise HTTPException(status_code=404, detail=permissions)
    
    return permissions


# 获取用户可访问页面
@router.get("/users/{user_id}/pages", response_model=Dict[str, Any])
async def get_user_pages(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户可访问页面
    """
    user_server = UserServerService(db)
    pages = user_server.get_user_pages(user_id)
    
    if "error" in pages:
        raise HTTPException(status_code=404, detail=pages)
    
    return pages


# 获取用户可访问任务
@router.get("/users/{user_id}/tasks", response_model=Dict[str, Any])
async def get_user_tasks(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户可访问任务
    """
    user_server = UserServerService(db)
    tasks = user_server.get_user_tasks(user_id)
    
    if "error" in tasks:
        raise HTTPException(status_code=404, detail=tasks)
    
    return tasks


# 获取用户资产列表
@router.get("/users/{user_id}/assets", response_model=List[Dict[str, Any]])
async def get_user_assets(
    user_id: int,
    asset_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    获取用户资产列表
    
    查询参数：
    - asset_type: 资产类型（可选，默认为None）
    """
    user_server = UserServerService(db)
    assets = user_server.get_user_assets(user_id, asset_type)
    
    return [{
        "id": asset.id,
        "user_id": asset.user_id,
        "asset_type": asset.asset_type,
        "asset_id": asset.asset_id,
        "like_count": asset.like_count,
        "created_at": asset.created_at.isoformat()
    } for asset in assets]


# 创建用户资产
@router.post("/users/{user_id}/assets", response_model=Dict[str, Any], status_code=201)
async def create_user_asset(
    user_id: int,
    asset_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    创建用户资产
    
    请求体参数：
    - asset_id: 资产ID（必填）
    - asset_type: 资产类型（可选，默认值为"post"）
    """
    user_server = UserServerService(db)
    
    # 验证必填字段
    if "asset_id" not in asset_data:
        raise HTTPException(status_code=400, detail={"error": "Missing required field: asset_id"})
    
    # 创建资产
    asset = user_server.create_asset(
        user_id=user_id,
        asset_id=asset_data["asset_id"],
        asset_type=asset_data.get("asset_type", "post")
    )
    
    if not asset:
        raise HTTPException(status_code=400, detail={"error": "Failed to create asset, may already exist"})
    
    return {
        "id": asset.id,
        "user_id": asset.user_id,
        "asset_type": asset.asset_type,
        "asset_id": asset.asset_id,
        "like_count": asset.like_count,
        "created_at": asset.created_at.isoformat()
    }


# 更新用户资产（点赞数）
@router.put("/users/{user_id}/assets/{asset_id}", response_model=Dict[str, Any])
async def update_user_asset(
    user_id: int,
    asset_id: str,
    asset_data: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """
    更新用户资产
    
    请求体参数：
    - like_count: 点赞数（必填）
    """
    user_server = UserServerService(db)
    
    # 验证必填字段
    if "like_count" not in asset_data:
        raise HTTPException(status_code=400, detail={"error": "Missing required field: like_count"})
    
    # 更新资产
    asset = user_server.update_asset_likes(asset_id, asset_data["like_count"])
    
    if not asset:
        raise HTTPException(status_code=404, detail={"error": "Asset not found"})
    
    return {
        "id": asset.id,
        "user_id": asset.user_id,
        "asset_type": asset.asset_type,
        "asset_id": asset.asset_id,
        "like_count": asset.like_count,
        "updated_at": asset.updated_at.isoformat()
    }


# 删除用户资产
@router.delete("/users/{user_id}/assets/{asset_id}", response_model=Dict[str, Any])
async def delete_user_asset(
    user_id: int,
    asset_id: str,
    db: Session = Depends(get_db)
):
    """
    删除用户资产
    """
    user_server = UserServerService(db)
    success = user_server.delete_asset(asset_id)
    
    if not success:
        raise HTTPException(status_code=404, detail={"error": "Asset not found"})
    
    return {
        "message": "Asset deleted successfully",
        "asset_id": asset_id
    }
