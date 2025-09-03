from fastapi import APIRouter, HTTPException, Query, Depends, Header, status
from typing import Optional, List, Dict, Any, Union, Annotated
from pydantic import BaseModel, EmailStr
from services.user_service import UserService
from dto.user_dto import (
    UserCreateDTO, UserUpdateDTO, UserLoginDTO, UserPasswordUpdateDTO,
    UserSearchDTO, UserFilterDTO, UserStatsDTO, UserRegistrationDTO,
    RefreshTokenDTO, TokenVerificationDTO, UserLoginResponseDTO, UserPaginatedResponseDTO
)
from dto.base_dto import SuccessResponseDTO, ErrorResponseDTO, PaginatedResponseDTO, PaginationDTO
from core.auth_middleware import get_current_user, require_role
from core.exceptions import NotFoundException, PermissionException, ValidationException, DuplicateException, ServiceException

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

# Helper function yang diperbaiki
# Helper function to handle service responses
def handle_service_response(result: Union[Dict[str, Any], SuccessResponseDTO, ErrorResponseDTO, PaginatedResponseDTO, UserLoginResponseDTO]):
    """Handle service response and convert to FastAPI response"""
    if isinstance(result, (SuccessResponseDTO, PaginatedResponseDTO, UserLoginResponseDTO)): # Add UserLoginResponseDTO here
        return result.dict(by_alias=True)
    elif isinstance(result, ErrorResponseDTO):
        status_code = result.status_code
        message = result.message
        raise HTTPException(status_code=status_code, detail=message)
    # This part of your code seems to handle dicts
    elif isinstance(result, dict):
        if result.get("success", True):
            return result.get("data", result)
        else:
            status_code = result.get("status_code", 500)
            message = result.get("message", "Internal server error")
            raise HTTPException(status_code=status_code, detail=message)
    else:
        raise HTTPException(status_code=500, detail="Unexpected response type from service.")

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

def get_token_from_header(authorization: Annotated[str, Header()]) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Header otorisasi tidak valid"
        )
    return authorization.split(" ")[1]


@user_router.post("/auth/logout", response_model=SuccessResponseDTO)
async def logout_user(
    token: str = Depends(get_token_from_header),
    # Kita panggil get_current_user untuk memastikan tokennya valid sebelum di-logout
    current_user: dict = Depends(get_current_user) 
):
    """Logout pengguna dengan menambahkan token ke blocklist."""
    success = user_service.logout_user(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal melakukan logout."
        )
        
    return SuccessResponseDTO(message="Logout berhasil")

# User profile endpoints
@user_router.get("/users/profile")
async def get_user_profile(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get current user profile"""
    try:
        # Dependency 'get_current_user' sudah menangani validasi token.
        # Kita tinggal ambil ID dari payload token yang dikembalikan.
        user_id = current_user.get("id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Token tidak valid atau tidak mengandung ID user")

        # Panggil service dengan ID user yang asli
        result = user_service.get_user_profile(user_id)
        
        # Di sini, kamu bisa menggunakan handle_service_response atau langsung return result
        # karena service sudah mengembalikan dictionary yang siap di-serialize.
        return result

    except NotFoundException as e:
        # Lebih baik menangani NotFoundException secara spesifik
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")


@user_router.put("/users/profile")
async def update_user_profile(
    # Langsung gunakan UserUpdateDTO yang sudah benar sebagai tipe data request body
    update_data: UserUpdateDTO,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Update user profile"""
    try:
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token tidak valid")

        # Tidak perlu konversi lagi, data sudah dalam format yang benar.
        # Langsung kirim ke service.
        result = user_service.update_user_profile(
            user_id,
            # Gunakan exclude_unset=True agar hanya field yang dikirim yang di-update
            update_data.dict(exclude_unset=True),
            user_id
        )

        return result

    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan: {str(e)}")

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
@user_router.get("/users", response_model=UserPaginatedResponseDTO)
async def get_users_list(
    # Hapus sort_by dan sort_order dari sini
    search: UserSearchDTO = Depends(),
    filter: UserFilterDTO = Depends(),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Get list of users (admin only)"""
    try:
        # Pindahkan sort_by dan sort_order ke dalam pagination_params
        # Ambil nilainya dari objek 'search'
        pagination_params = {
            "page": page,
            "limit": limit,
            "sort_by": search.sort_by or "created_at", # Ambil dari DTO
            "sort_order": search.sort_order or "desc"  # Ambil dari DTO
        }

        # Panggil service dengan parameter yang sudah disesuaikan
        result = user_service.get_users_list(
            # Gunakan exclude_unset=True agar parameter opsional yang kosong tidak dikirim
            search_params=search.dict(exclude_unset=True),
            filter_params=filter.dict(exclude_unset=True),
            pagination=pagination_params,
            current_user_id=current_user.get("id")
        )
        
        return result

    except (NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        import traceback
        print(traceback.format_exc()) # Tambahkan ini untuk debugging
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

@user_router.patch("/users/{user_id}/activate", response_model=SuccessResponseDTO)
async def activate_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Activate user (admin only)"""
    try:
        result = user_service.activate_user(
            user_id_to_activate=user_id,
            current_user_id=current_user.get("id")
        )
        return SuccessResponseDTO(
            data=result,
            message="Pengguna berhasil diaktifkan"
        )
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan tak terduga: {str(e)}")
    

@user_router.patch("/users/{user_id}/deactivate", response_model=SuccessResponseDTO)
async def deactivate_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Deactivate user (admin only)"""
    try:
        # Panggil service dengan menyertakan ID admin yang melakukan aksi
        result = user_service.deactivate_user(
            user_id=user_id,
            current_user_id=current_user.get("id")
        )
        return SuccessResponseDTO(
            data=result,
            message="Pengguna berhasil dinonaktifkan"
        )
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except PermissionException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan tak terduga: {str(e)}")

@user_router.delete("/users/{user_id}", response_model=SuccessResponseDTO)
async def delete_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_role("admin"))
):
    """Delete user (admin only)"""
    try:
        # Panggil service dengan menyertakan ID admin yang melakukan aksi
        result = user_service.delete_user(
            user_id_to_delete=user_id,
            current_user_id=current_user.get("id")
        )
        return SuccessResponseDTO(
            data=result,
            message="Pengguna berhasil dihapus"
        )
    except (NotFoundException, ValidationException) as e:
        raise HTTPException(status_code=404, detail=str(e)) # 404 jika user tidak ditemukan
    except PermissionException as e:
        raise HTTPException(status_code=403, detail=str(e)) # 403 jika mencoba hapus diri sendiri
    except ServiceException as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan tak terduga: {str(e)}")

# Export router
__all__ = ["user_router"]