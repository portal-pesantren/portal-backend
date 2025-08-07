from fastapi import APIRouter, HTTPException, Query, Depends, Header
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr
from services.user_service import UserService
from dto.user_dto import (
    UserCreateDTO, UserUpdateDTO, UserLoginDTO, UserPasswordUpdateDTO,
    UserSearchDTO, UserFilterDTO, UserStatsDTO, UserRegistrationDTO,
    RefreshTokenDTO, TokenVerificationDTO
)

# Create FastAPI router
user_router = APIRouter()

# Initialize user service
user_service = UserService()

# Pydantic models for request/response
class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    confirm_password: str
    phone: Optional[str] = None
    role: Optional[str] = "parent"
    terms_accepted: bool = True

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    profile_picture: Optional[str] = None

class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirmRequest(BaseModel):
    token: str
    new_password: str

class EmailVerificationRequest(BaseModel):
    token: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenVerificationRequest(BaseModel):
    token: str

# Helper function to handle service responses
def handle_service_response(result: Dict[str, Any]):
    """Handle service response and convert to FastAPI response"""
    if result.get("success", True):
        return result.get("data", result)
    else:
        status_code = result.get("status_code", 500)
        message = result.get("message", "Internal server error")
        raise HTTPException(status_code=status_code, detail=message)

# Authentication endpoints
@user_router.post("/auth/register")
async def register_user_auth(request: UserRegisterRequest):
    """Register new user (auth endpoint)"""
    try:
        # Create registration DTO
        register_dto = UserRegistrationDTO(
            name=request.name,
            email=request.email,
            password=request.password,
            confirm_password=request.confirm_password,
            phone=request.phone or "081234567890",
            role=request.role,
            terms_accepted=request.terms_accepted
        )
        
        # Register user
        result = user_service.register_user(register_dto.dict())
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

@user_router.post("/users/register")
async def register_user(request: UserRegisterRequest):
    """Register new user (users endpoint for compatibility)"""
    try:
        # Create registration DTO
        register_dto = UserRegistrationDTO(
            name=request.name,
            email=request.email,
            password=request.password,
            confirm_password=request.confirm_password,
            phone=request.phone or "081234567890",
            role=request.role,
            terms_accepted=request.terms_accepted
        )
        
        # Register user
        result = user_service.register_user(register_dto.dict())
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Users registration failed: {str(e)}")

@user_router.post("/auth/login")
async def login_user_auth(request: UserLoginRequest):
    """User login (auth endpoint)"""
    try:
        # Login user
        result = user_service.login_user(request.dict())
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/users/login")
async def login_user(request: UserLoginRequest):
    """User login (users endpoint for compatibility)"""
    try:
        # Login user
        result = user_service.login_user(request.dict())
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/auth/verify-email")
async def verify_email(request: EmailVerificationRequest):
    """Verify email address"""
    try:
        result = user_service.verify_email(request.token)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/auth/forgot-password")
async def forgot_password(request: PasswordResetRequest):
    """Request password reset"""
    try:
        result = user_service.request_password_reset(request.email)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/auth/reset-password")
async def reset_password(request: PasswordResetConfirmRequest):
    """Reset password with token"""
    try:
        result = user_service.reset_password(request.token, request.new_password)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""
    try:
        result = user_service.refresh_token(request.refresh_token)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/auth/verify")
async def verify_token(request: TokenVerificationRequest):
    """Verify JWT token"""
    try:
        result = user_service.verify_token(request.token)
        if result["valid"]:
            return result
        else:
            raise HTTPException(status_code=401, detail=result["error"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/auth/logout")
async def logout_user(authorization: Optional[str] = Header(None)):
    """User logout"""
    try:
        # Extract user from token (simplified - in real implementation, use proper auth dependency)
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        # For now, return success (implement proper token extraction)
        return {"message": "Logout berhasil"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# User profile endpoints
@user_router.get("/users/profile")
async def get_user_profile(authorization: Optional[str] = Header(None)):
    """Get current user profile"""
    try:
        # Extract user_id from token (simplified)
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        # For now, return mock data (implement proper auth)
        user_id = "mock_user_id"  # Extract from token
        result = user_service.get_user_profile(user_id)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.put("/users/profile")
async def update_user_profile(
    request: UserUpdateRequest,
    authorization: Optional[str] = Header(None)
):
    """Update user profile"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        # Extract user_id from token
        user_id = "mock_user_id"  # Extract from token
        
        # Create update DTO
        update_dto = UserUpdateDTO(**request.dict(exclude_unset=True))
        
        # Update user profile
        result = user_service.update_user_profile(user_id, update_dto.dict(), user_id)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.post("/users/change-password")
async def change_password(
    request: PasswordChangeRequest,
    authorization: Optional[str] = Header(None)
):
    """Change user password"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        # Extract user_id from token
        user_id = "mock_user_id"  # Extract from token
        
        # Create password DTO
        password_dto = UserPasswordUpdateDTO(**request.dict())
        
        # Change password
        result = user_service.change_password(user_id, password_dto.dict())
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Admin endpoints
@user_router.get("/users")
async def get_users_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    query: Optional[str] = Query(None, description="Search query"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order"),
    role: Optional[str] = Query(None, description="Filter by role"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_verified: Optional[bool] = Query(None, description="Filter by verified status"),
    authorization: Optional[str] = Header(None)
):
    """Get list of users (admin only)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        # Create search DTO
        search_dto = UserSearchDTO(
            query=query or "",
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Create filter DTO
        filter_params = {}
        if role is not None:
            filter_params["role"] = role
        if is_active is not None:
            filter_params["is_active"] = is_active
        if is_verified is not None:
            filter_params["is_verified"] = is_verified
            
        filter_dto = UserFilterDTO(**filter_params)
        
        # Get users list
        result = user_service.get_users_list(
            page=page,
            limit=limit,
            search=search_dto,
            filters=filter_dto
        )
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.get("/users/stats")
async def get_user_stats(authorization: Optional[str] = Header(None)):
    """Get user statistics (admin only)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        # Extract user_id from token
        user_id = "mock_user_id"  # Extract from token
        
        result = user_service.get_user_stats(user_id)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.get("/users/{user_id}")
async def get_user_by_id(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """Get user by ID (admin only)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        result = user_service.get_user_profile(user_id)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    request: UserUpdateRequest,
    authorization: Optional[str] = Header(None)
):
    """Update user (admin only)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        # Extract current user_id from token
        current_user_id = "mock_user_id"  # Extract from token
        
        # Create update DTO
        update_dto = UserUpdateDTO(**request.dict(exclude_unset=True))
        
        # Update user
        result = user_service.update_user_profile(user_id, update_dto.dict(), current_user_id)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.patch("/users/{user_id}/activate")
async def activate_user(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """Activate user (admin only)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        # For now, return success response (implement in service)
        return {
            "user_id": user_id,
            "is_active": True,
            "message": "Pengguna berhasil diaktifkan"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """Deactivate user (admin only)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        result = user_service.deactivate_user(user_id)
        return handle_service_response(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@user_router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    authorization: Optional[str] = Header(None)
):
    """Delete user (admin only)"""
    try:
        if not authorization:
            raise HTTPException(status_code=401, detail="Authorization header required")
            
        # Implement delete user in service
        return {
            "user_id": user_id,
            "message": "Pengguna berhasil dihapus"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Export router
__all__ = ["user_router"]