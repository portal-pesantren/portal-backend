from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# Create FastAPI router
user_router = APIRouter()

# Pydantic models for request/response
class UserRegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: Optional[str] = "user"
    is_active: bool = True

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserUpdateRequest(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    phone: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str

# User authentication endpoints
@user_router.post("/users/register")
async def register_user(request: UserRegisterRequest):
    """Register new user"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.register_user(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/users/login")
async def login_user(request: UserLoginRequest):
    """User login"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.login_user(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/users/logout")
async def logout_user():
    """User logout"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        return await router_instance.logout_user({})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/users/refresh-token")
async def refresh_token():
    """Refresh access token"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        return await router_instance.refresh_token({})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User profile endpoints
@user_router.get("/users/profile")
async def get_user_profile():
    """Get current user profile"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        return await router_instance.get_user_profile({})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.put("/users/profile")
async def update_user_profile(request: UserUpdateRequest):
    """Update user profile"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        context = {
            "data": request.dict(exclude_unset=True)
        }
        
        return await router_instance.update_user_profile(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/users/change-password")
async def change_password(request: PasswordChangeRequest):
    """Change user password"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.change_password(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/users/reset-password")
async def reset_password(request: PasswordResetRequest):
    """Request password reset"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.reset_password(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/users/reset-password/confirm")
async def confirm_password_reset(request: PasswordResetConfirmRequest):
    """Confirm password reset"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.confirm_password_reset(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User management endpoints (admin)
@user_router.get("/users")
async def get_users_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """Get list of users (admin only)"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit,
                "search": search,
                "role": role,
                "is_active": is_active
            }
        }
        
        return await router_instance.get_users_list(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.get("/users/stats")
async def get_user_stats():
    """Get user statistics (admin only)"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        return await router_instance.get_user_stats({})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.get("/users/{user_id}")
async def get_user_by_id(user_id: str):
    """Get user by ID (admin only)"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        return await router_instance.get_user_by_id(user_id, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.put("/users/{user_id}")
async def update_user(user_id: str, request: UserUpdateRequest):
    """Update user (admin only)"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        context = {
            "data": request.dict(exclude_unset=True)
        }
        
        return await router_instance.update_user(user_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.patch("/users/{user_id}/activate")
async def activate_user(user_id: str):
    """Activate user (admin only)"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        return await router_instance.activate_user(user_id, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.patch("/users/{user_id}/deactivate")
async def deactivate_user(user_id: str):
    """Deactivate user (admin only)"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        return await router_instance.deactivate_user(user_id, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    """Delete user (admin only)"""
    try:
        from routers.user_router import UserRouter
        router_instance = UserRouter()
        
        return await router_instance.delete_user(user_id, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))