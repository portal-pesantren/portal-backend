from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
import secrets
import logging

# Import your models and services
from models.user import UserModel
from services.jwt_service import JWTService
from .base_service import BaseService
from models.token_blocklist import TokenBlocklistModel

# Import your custom exceptions
from core.exceptions import NotFoundException, DuplicateException, ValidationException, PermissionException, ServiceException

class UserService(BaseService[Any, UserModel]):
    """Service untuk mengelola pengguna."""
    
    def __init__(self):
        super().__init__(UserModel)
        self.jwt_service = JWTService()
    
    def get_resource_name(self) -> str:
        return "User"

    def register_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Registrasi pengguna baru."""
        sanitized_data = data.copy()
        sanitized_data.pop('confirm_password', None)
        sanitized_data.pop('terms_accepted', None)
        
        sanitized_data = self.sanitize_input(sanitized_data)
        
        existing_email = self.model.find_one({"email": sanitized_data["email"]})
        if existing_email:
            raise DuplicateException("User", "email", sanitized_data["email"])
        
        if sanitized_data.get("phone"):
            existing_phone = self.model.find_one({"phone": sanitized_data["phone"]})
            if existing_phone:
                raise DuplicateException("User", "phone", sanitized_data["phone"])
        
        user_data = {
            **sanitized_data,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        user = self.model.create_user(user_data)
        
        self.log_activity(user["id"], "register", "user", user["id"])
        
        access_token = self.jwt_service.create_access_token(user)
        refresh_token = self.jwt_service.create_refresh_token(user)
        
        # Return a dictionary with all the necessary data for the router
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": self.jwt_service.access_token_expire_minutes * 60,
            "token_type": "Bearer"
        }
    
    def login_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Login pengguna."""
        user = self.model.authenticate_user(data["email"], data["password"])
        if not user:
            raise ValidationException("Email atau password tidak valid")
        
        if not user.get("is_active", True):
            raise ValidationException("Akun Anda telah dinonaktifkan")
            
        user_id = user["id"]
        
        self.model.update_by_id(user_id, {
            "last_login": datetime.now(),
            "login_count": user.get("login_count", 0) + 1
        })
        
        self.log_activity(user_id, "login", "user", user_id)
        
        access_token = self.jwt_service.create_access_token(user)
        refresh_token = self.jwt_service.create_refresh_token(user)
        
        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": self.jwt_service.access_token_expire_minutes * 60,
            "token_type": "Bearer"
        }
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token menggunakan refresh token."""
        payload = self.jwt_service.verify_token(refresh_token, "refresh")
        user_id = payload.get("user_id")
        
        user = self.model.find_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        if not user.get("is_active", True):
            raise PermissionException("Akun telah dinonaktifkan", "refresh token")
        
        new_access_token = self.jwt_service.create_access_token(user)
        
        self.log_activity(user_id, "refresh_token", "user", user_id)
        
        return {
            "access_token": new_access_token,
            "expires_in": self.jwt_service.access_token_expire_minutes * 60,
            "token_type": "Bearer"
        }
    
    def logout_user(self, token: str) -> bool:
        """Logout pengguna dengan menambahkan token ke blocklist."""
        try:
            # Decode token untuk mendapatkan payload
            payload = self.jwt_service.verify_token(token)
            
            jti = payload.get("jti")
            exp = payload.get("exp")
            
            if not jti or not exp:
                return False

            # Konversi timestamp 'exp' menjadi objek datetime
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            
            # Panggil model untuk memblokir token
            blocklist_model = TokenBlocklistModel()
            return blocklist_model.block_token(jti, expires_at)
        except Exception as e:
            logging.error(f"Error during logout: {e}", exc_info=True)
            return False
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verifikasi JWT token."""
        payload = self.jwt_service.verify_token(token, "access")
        user_id = payload.get("user_id")
        user = self.model.find_by_id(user_id)
        
        if not user:
            raise NotFoundException("User", user_id)
        
        if not user.get("is_active", True):
            raise PermissionException("Akun telah dinonaktifkan", "access token")
        
        user.pop("password", None)
        return {"valid": True, "user": user, "payload": payload}

    def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Mendapatkan profil pengguna."""
        user = self.model.find_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
        
        user.pop("password", None)
        return user

    def update_user_profile(
        self, 
        user_id: str, 
        data: Dict[str, Any], 
        current_user_id: str
    ) -> Dict[str, Any]:
        """Update profil pengguna."""
        user_to_update = self.model.find_by_id(user_id)
        if not user_to_update:
            raise NotFoundException("User", user_id)
            
        if user_id != current_user_id:
            current_user = self.model.find_by_id(current_user_id)
            if not current_user or current_user.get("role") not in ["admin", "super_admin"]:
                raise PermissionException("update", "user profile")
        
        sanitized_data = self.sanitize_input(data)
        
        if "email" in sanitized_data and sanitized_data["email"] != user_to_update.get("email"):
            existing = self.model.find_one({"email": sanitized_data["email"]})
            if existing:
                raise DuplicateException("User", "email", sanitized_data["email"])
            
        if "phone" in sanitized_data and sanitized_data.get("phone") != user_to_update.get("phone"):
            existing = self.model.find_one({"phone": sanitized_data["phone"]})
            if existing:
                raise DuplicateException("User", "phone", sanitized_data["phone"])
                
        sanitized_data["updated_at"] = datetime.now()
        
        # Langkah 1: Lakukan update dan periksa hasilnya (boolean)
        was_successful = self.model.update_profile(user_id, sanitized_data)
        if not was_successful:
            # Gagal memperbarui di level database
            raise Exception("Gagal memperbarui profil di database")
            
        self.log_activity(current_user_id, "update_profile", "user", user_id, sanitized_data)
        
        # Langkah 2: Jika berhasil, ambil kembali data user yang sudah ter-update
        updated_user_document = self.model.find_by_id(user_id)
        if not updated_user_document:
            raise NotFoundException("User yang baru diupdate tidak ditemukan", user_id)

        # Langkah 3: Hapus field password dari dokumen yang baru diambil
        updated_user_document.pop("password", None)
        
        # Langkah 4: Kembalikan dokumen tersebut
        return updated_user_document
    
    def change_password(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mengubah password pengguna."""
        user = self.model.find_by_id(user_id)
        if not user:
            raise NotFoundException("User", user_id)
            
        if not self.model._verify_password(data.get("current_password"), user["password"]):
            raise ValidationException("Password saat ini tidak valid")
        
        success = self.model.update_password(user_id, data.get("new_password"))
        if not success:
            raise Exception("Gagal mengubah password")
        
        self.log_activity(user_id, "change_password", "user", user_id)
        
        return {"id": user_id, "message": "Password berhasil diubah"}
    
    def get_users_list(
        self,
        search_params: Optional[Dict[str, Any]] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None,
        current_user_id: str = None
    ) -> Dict[str, Any]:
        """Mendapatkan daftar pengguna (admin only)."""
        current_user = self.model.find_by_id(current_user_id)
        if not current_user or current_user.get("role") != "admin":
            raise PermissionException("view", "user list")

        query = {}
        if search_params and search_params.get("query"):
            query["$or"] = [
                {"name": {"$regex": search_params["query"], "$options": "i"}},
                {"email": {"$regex": search_params["query"], "$options": "i"}}
            ]
        
        if filter_params:
            if filter_params.get("role"):
                query["role"] = filter_params["role"]
            if filter_params.get("is_active") is not None:
                query["is_active"] = filter_params["is_active"]
            if filter_params.get("is_verified") is not None:
                query["is_verified"] = filter_params["is_verified"]

        pagination_dto = pagination if pagination else {}
        page = pagination_dto.get("page", 1)
        limit = pagination_dto.get("limit", 10)
        sort_by = pagination_dto.get("sort_by", "created_at")
        sort_order = pagination_dto.get("sort_order", "desc")
        
        skip = (page - 1) * limit
        sort_criteria = [(sort_by, 1 if sort_order == "asc" else -1)]

        users = self.model.find_many(
            filter_dict=query,
            sort=sort_criteria, 
            limit=limit, 
            skip=skip
        )
        total = self.model.count(filter_dict=query)

        for user in users:
            user.pop("password", None)
            user.pop("email_verification_token", None)
            user.pop("phone_verification_token", None)
            user.pop("password_reset_token", None)
            
        return {
            "data": users,
            "total": total,
            "page": page,
            "limit": limit
        }
    
    def get_user_stats(self, current_user_id: str) -> Dict[str, Any]:
        """Mendapatkan statistik pengguna (admin only)."""
        current_user = self.model.find_by_id(current_user_id)
        if not current_user or current_user.get("role") != "admin":
            raise PermissionException("view", "user statistics")
        
        stats = self.model.get_user_stats()
        return stats
    
    def activate_user(self, user_id_to_activate: str, current_user_id: str) -> Dict[str, Any]:
        """Aktivasi pengguna oleh admin."""
        # Cek izin: Pastikan yang melakukan aksi adalah admin
        current_user = self.model.find_by_id(current_user_id)
        if not current_user or current_user.get("role") not in ["admin", "super_admin"]:
            raise PermissionException("activate", "user")

        # Cek apakah user yang akan diaktifkan ada
        user_to_activate = self.model.find_by_id(user_id_to_activate)
        if not user_to_activate:
            raise NotFoundException("User", user_id_to_activate)

        # Panggil metode model untuk melakukan update
        success = self.model.activate_user(user_id_to_activate)
        if not success:
            raise ServiceException("Gagal mengaktifkan pengguna di database")

        # Catat aktivitas
        self.log_activity(current_user_id, "activate", "user", user_id_to_activate)
        
        return {"id": user_id_to_activate, "is_active": True}

    def deactivate_user(
        self, 
        user_id: str, 
        current_user_id: str
    ) -> Dict[str, Any]:
        """Deaktivasi pengguna (admin only)."""
        current_user = self.model.find_by_id(current_user_id)
        if not current_user or current_user.get("role") not in ["admin", "super_admin"]:
            raise PermissionException("deactivate", "user")
        
        self.check_exists(user_id, "User")
        
        success = self.model.deactivate_user(user_id)
        if not success:
            raise ServiceException("Gagal menonaktifkan pengguna")
        
        self.log_activity(current_user_id, "deactivate", "user", user_id)
        
        return {"id": user_id, "message": "Pengguna berhasil dinonaktifkan"}
    
    
    def delete_user(self, user_id_to_delete: str, current_user_id: str) -> Dict[str, Any]:
        """Menghapus pengguna oleh admin."""
        # Cek izin: Pastikan yang melakukan aksi adalah admin
        current_user = self.model.find_by_id(current_user_id)
        if not current_user or current_user.get("role") not in ["admin", "super_admin"]:
            raise PermissionException("delete", "user")

        # PENTING: Cegah admin menghapus akunnya sendiri
        if user_id_to_delete == current_user_id:
            raise PermissionException("delete", "your own account")

        # Cek apakah user yang akan dihapus ada
        user_to_delete = self.model.find_by_id(user_id_to_delete)
        if not user_to_delete:
            raise NotFoundException("User", user_id_to_delete)

        # Panggil metode model untuk menghapus
        success = self.model.delete_by_id(user_id_to_delete)
        if not success:
            raise ServiceException("Gagal menghapus pengguna dari database")

        # Catat aktivitas
        self.log_activity(current_user_id, "delete", "user", user_id_to_delete)
        
        return {"id": user_id_to_delete, "deleted": True}