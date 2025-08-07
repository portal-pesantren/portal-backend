from typing import Optional, Dict, Any
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.jwt_service import JWTService
from models.user import UserModel
from core.exceptions import ValidationException

# Security scheme
security = HTTPBearer()

# JWT Service instance
jwt_service = JWTService()
user_model = UserModel()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Dependency untuk mendapatkan user yang sedang login dari JWT token
    
    Args:
        credentials: HTTP Authorization credentials
        
    Returns:
        Dict[str, Any]: Data user yang sedang login
        
    Raises:
        HTTPException: Jika token tidak valid atau user tidak ditemukan
    """
    try:
        # Extract token
        token = credentials.credentials
        
        # Verify token
        payload = jwt_service.verify_token(token, "access")
        
        # Get user from database
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token tidak valid: user_id tidak ditemukan",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = user_model.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User tidak ditemukan",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Akun telah dinonaktifkan",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Remove sensitive data
        user.pop("password", None)
        user.pop("email_verification_token", None)
        user.pop("phone_verification_token", None)
        user.pop("password_reset_token", None)
        
        return user
        
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Dependency untuk mendapatkan user aktif yang sedang login
    
    Args:
        current_user: User yang sedang login
        
    Returns:
        Dict[str, Any]: Data user yang sedang login dan aktif
        
    Raises:
        HTTPException: Jika user tidak aktif
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User tidak aktif"
        )
    return current_user

def require_role(required_role: str):
    """
    Decorator untuk memerlukan role tertentu
    
    Args:
        required_role: Role yang diperlukan
        
    Returns:
        Function: Dependency function
    """
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Role {required_role} diperlukan"
            )
        return current_user
    return role_checker

def require_roles(required_roles: list):
    """
    Decorator untuk memerlukan salah satu dari beberapa role
    
    Args:
        required_roles: List role yang diperlukan
        
    Returns:
        Function: Dependency function
    """
    def roles_checker(current_user: Dict[str, Any] = Depends(get_current_active_user)) -> Dict[str, Any]:
        user_role = current_user.get("role")
        if user_role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Akses ditolak. Salah satu role berikut diperlukan: {', '.join(required_roles)}"
            )
        return current_user
    return roles_checker

def get_optional_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """
    Dependency untuk mendapatkan user yang sedang login (opsional)
    Tidak akan raise error jika token tidak ada atau tidak valid
    
    Args:
        credentials: HTTP Authorization credentials (optional)
        
    Returns:
        Optional[Dict[str, Any]]: Data user yang sedang login atau None
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None
    except Exception:
        return None