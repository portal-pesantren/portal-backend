from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import jwt
import os
from dotenv import load_dotenv
from core.exceptions import ValidationException

load_dotenv()

class JWTService:
    """Service untuk mengelola JWT tokens"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire_minutes = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
        self.refresh_token_expire_days = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """
        Membuat access token JWT
        
        Args:
            user_data: Data pengguna yang akan disimpan dalam token
            
        Returns:
            str: JWT access token
        """
        # Prepare payload
        payload = {
            "user_id": str(user_data.get("id") or user_data.get("_id")),
            "email": user_data.get("email"),
            "role": user_data.get("role"),
            "name": user_data.get("name"),
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
            "iat": datetime.utcnow(),
            "type": "access"
        }
        
        # Create token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """
        Membuat refresh token JWT
        
        Args:
            user_data: Data pengguna yang akan disimpan dalam token
            
        Returns:
            str: JWT refresh token
        """
        # Prepare payload
        payload = {
            "user_id": str(user_data.get("id") or user_data.get("_id")),
            "email": user_data.get("email"),
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
            "iat": datetime.utcnow(),
            "type": "refresh"
        }
        
        # Create token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        return token
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """
        Memverifikasi dan mendecode JWT token
        
        Args:
            token: JWT token yang akan diverifikasi
            token_type: Tipe token (access atau refresh)
            
        Returns:
            Dict[str, Any]: Payload token yang sudah didecode
            
        Raises:
            ValidationException: Jika token tidak valid
        """
        try:
            # Decode token
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verify token type
            if payload.get("type") != token_type:
                raise ValidationException(f"Token type mismatch. Expected {token_type}")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ValidationException("Token telah kedaluwarsa")
        except jwt.InvalidTokenError:
            raise ValidationException("Token tidak valid")
        except Exception as e:
            raise ValidationException(f"Error verifying token: {str(e)}")
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """
        Membuat access token baru menggunakan refresh token
        
        Args:
            refresh_token: Refresh token yang valid
            
        Returns:
            str: Access token baru
            
        Raises:
            ValidationException: Jika refresh token tidak valid
        """
        # Verify refresh token
        payload = self.verify_token(refresh_token, "refresh")
        
        # Create new access token
        user_data = {
            "id": payload.get("user_id"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "name": payload.get("name")
        }
        
        return self.create_access_token(user_data)
    
    def get_token_payload(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan payload token tanpa verifikasi (untuk debugging)
        
        Args:
            token: JWT token
            
        Returns:
            Optional[Dict[str, Any]]: Payload token atau None jika gagal
        """
        try:
            # Decode without verification
            payload = jwt.decode(token, options={"verify_signature": False})
            return payload
        except Exception:
            return None
    
    def is_token_expired(self, token: str) -> bool:
        """
        Mengecek apakah token sudah kedaluwarsa
        
        Args:
            token: JWT token
            
        Returns:
            bool: True jika token kedaluwarsa
        """
        try:
            payload = self.get_token_payload(token)
            if not payload:
                return True
            
            exp = payload.get("exp")
            if not exp:
                return True
            
            return datetime.utcnow().timestamp() > exp
        except Exception:
            return True