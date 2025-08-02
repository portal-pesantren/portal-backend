from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import secrets
from models.user import UserModel
from dto.user_dto import (
    UserCreateDTO,
    UserUpdateDTO,
    UserPasswordUpdateDTO,
    UserLoginDTO,
    UserResponseDTO,
    UserProfileDTO,
    UserSearchDTO,
    UserFilterDTO,
    UserStatsDTO,
    UserLoginResponseDTO,
    UserRegistrationDTO,
    UserVerificationDTO,
    UserForgotPasswordDTO,
    UserResetPasswordDTO
)
from dto.base_dto import PaginationDTO, PaginatedResponseDTO, SuccessResponseDTO
from .base_service import BaseService, NotFoundException, DuplicateException, ValidationException, PermissionException

class UserService(BaseService[UserCreateDTO, UserModel]):
    """Service untuk mengelola pengguna"""
    
    def __init__(self):
        super().__init__(UserModel)
    
    def get_resource_name(self) -> str:
        return "User"
    
    def register_user(self, data: Dict[str, Any]) -> SuccessResponseDTO:
        """Registrasi pengguna baru"""
        try:
            # Validasi input menggunakan DTO
            register_dto = self.validate_dto(UserRegistrationDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(register_dto.dict())
            
            # Check duplicate email
            existing_email = self.model.find_one({"email": sanitized_data["email"]})
            if existing_email:
                raise DuplicateException("User", "email", sanitized_data["email"])
            
            # Check duplicate phone if provided
            if sanitized_data.get("phone"):
                existing_phone = self.model.find_one({"phone": sanitized_data["phone"]})
                if existing_phone:
                    raise DuplicateException("User", "phone", sanitized_data["phone"])
            
            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            
            # Prepare user data
            user_data = {
                "name": sanitized_data["name"],
                "email": sanitized_data["email"],
                "phone": sanitized_data.get("phone"),
                "password": sanitized_data["password"],  # Will be hashed in model
                "role": sanitized_data.get("role", "parent"),
                "is_active": True,
                "is_email_verified": False,
                "is_phone_verified": False,
                "email_verification_token": verification_token,
                "email_verification_expires": datetime.now() + timedelta(hours=24),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Create user
            user = self.model.create_user(user_data)
            
            # Remove sensitive data from response
            user.pop("password", None)
            user.pop("email_verification_token", None)
            
            # Log activity
            self.log_activity(user["_id"], "register", "user", user["_id"])
            
            # Convert to response DTO
            response_data = UserResponseDTO(**user)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Registrasi berhasil. Silakan cek email untuk verifikasi.",
                meta={"verification_token": verification_token}  # For testing purposes
            )
            
        except ValidationException as e:
            return self.create_validation_error_response(e.errors)
        except DuplicateException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal melakukan registrasi",
                code="REGISTRATION_ERROR"
            )
    
    def login_user(self, data: Dict[str, Any]) -> SuccessResponseDTO:
        """Login pengguna"""
        try:
            # Validasi input
            login_dto = self.validate_dto(UserLoginDTO, data)
            
            # Authenticate user
            user = self.model.authenticate_user(login_dto.email, login_dto.password)
            if not user:
                return self.create_error_response(
                    message="Email atau password tidak valid",
                    code="INVALID_CREDENTIALS"
                )
            
            # Check if user is active
            if not user.get("is_active", True):
                return self.create_error_response(
                    message="Akun Anda telah dinonaktifkan",
                    code="ACCOUNT_DISABLED"
                )
            
            # Update last login
            self.model.update_by_id(user["_id"], {
                "last_login": datetime.now(),
                "login_count": user.get("login_count", 0) + 1
            })
            
            # Generate access token (simplified - in real app use JWT)
            access_token = secrets.token_urlsafe(32)
            refresh_token = secrets.token_urlsafe(32)
            
            # Log activity
            self.log_activity(user["_id"], "login", "user", user["_id"])
            
            # Prepare response
            user_profile = UserProfileDTO(**user)
            login_response = UserLoginResponseDTO(
                user=user_profile,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=3600,  # 1 hour
                token_type="Bearer"
            )
            
            return self.create_success_response(
                data=login_response.dict(),
                message="Login berhasil"
            )
            
        except ValidationException as e:
            return self.create_validation_error_response(e.errors)
        except Exception as e:
            return self.create_error_response(
                message="Gagal melakukan login",
                code="LOGIN_ERROR"
            )
    
    def get_user_profile(self, user_id: str) -> SuccessResponseDTO:
        """Mendapatkan profil pengguna"""
        try:
            user = self.model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            # Remove sensitive data
            user.pop("password", None)
            user.pop("email_verification_token", None)
            user.pop("phone_verification_token", None)
            user.pop("password_reset_token", None)
            
            response_data = UserProfileDTO(**user)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Profil pengguna berhasil diambil"
            )
            
        except NotFoundException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil profil pengguna",
                code="PROFILE_ERROR"
            )
    
    def update_user_profile(
        self, 
        user_id: str, 
        data: Dict[str, Any], 
        current_user_id: str
    ) -> SuccessResponseDTO:
        """Update profil pengguna"""
        try:
            # Check permission
            if user_id != current_user_id:
                # Only admin can update other users
                current_user = self.model.find_by_id(current_user_id)
                if not current_user or current_user.get("role") != "admin":
                    raise PermissionException("update", "user profile")
            
            # Check if user exists
            self.check_exists(user_id, "User")
            
            # Validasi input
            update_dto = self.validate_dto(UserUpdateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(update_dto.dict(exclude_unset=True))
            
            # Check duplicate email if email is being updated
            if "email" in sanitized_data:
                existing = self.model.find_one({
                    "email": sanitized_data["email"],
                    "_id": {"$ne": user_id}
                })
                if existing:
                    raise DuplicateException("User", "email", sanitized_data["email"])
                
                # Reset email verification if email changed
                sanitized_data["is_email_verified"] = False
                sanitized_data["email_verification_token"] = secrets.token_urlsafe(32)
                sanitized_data["email_verification_expires"] = datetime.now() + timedelta(hours=24)
            
            # Check duplicate phone if phone is being updated
            if "phone" in sanitized_data:
                existing = self.model.find_one({
                    "phone": sanitized_data["phone"],
                    "_id": {"$ne": user_id}
                })
                if existing:
                    raise DuplicateException("User", "phone", sanitized_data["phone"])
                
                # Reset phone verification if phone changed
                sanitized_data["is_phone_verified"] = False
            
            # Add update metadata
            sanitized_data["updated_at"] = datetime.now()
            
            # Update user
            updated_user = self.model.update_profile(user_id, sanitized_data)
            
            # Log activity
            self.log_activity(current_user_id, "update_profile", "user", user_id, sanitized_data)
            
            # Remove sensitive data
            updated_user.pop("password", None)
            updated_user.pop("email_verification_token", None)
            updated_user.pop("phone_verification_token", None)
            updated_user.pop("password_reset_token", None)
            
            response_data = UserProfileDTO(**updated_user)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Profil berhasil diperbarui"
            )
            
        except (ValidationException, NotFoundException, DuplicateException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memperbarui profil",
                code="UPDATE_PROFILE_ERROR"
            )
    
    def change_password(
        self, 
        user_id: str, 
        data: Dict[str, Any]
    ) -> SuccessResponseDTO:
        """Mengubah password pengguna"""
        try:
            # Validasi input
            password_dto = self.validate_dto(UserPasswordUpdateDTO, data)
            
            # Get current user
            user = self.model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            # Verify current password
            if not self.model.verify_password(password_dto.current_password, user["password"]):
                return self.create_error_response(
                    message="Password saat ini tidak valid",
                    code="INVALID_CURRENT_PASSWORD"
                )
            
            # Update password
            success = self.model.update_password(user_id, password_dto.new_password)
            if not success:
                return self.create_error_response(
                    message="Gagal mengubah password",
                    code="PASSWORD_UPDATE_ERROR"
                )
            
            # Log activity
            self.log_activity(user_id, "change_password", "user", user_id)
            
            return self.create_success_response(
                data={"id": user_id},
                message="Password berhasil diubah"
            )
            
        except (ValidationException, NotFoundException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengubah password",
                code="CHANGE_PASSWORD_ERROR"
            )
    
    def verify_email(self, data: Dict[str, Any]) -> SuccessResponseDTO:
        """Verifikasi email pengguna"""
        try:
            # Validasi input
            verify_dto = self.validate_dto(UserVerificationDTO, data)
            
            # Find user by token
            user = self.model.find_one({
                "email_verification_token": verify_dto.token,
                "email_verification_expires": {"$gt": datetime.now()}
            })
            
            if not user:
                return self.create_error_response(
                    message="Token verifikasi tidak valid atau sudah kadaluarsa",
                    code="INVALID_VERIFICATION_TOKEN"
                )
            
            # Verify email
            success = self.model.verify_email(user["_id"])
            if not success:
                return self.create_error_response(
                    message="Gagal memverifikasi email",
                    code="EMAIL_VERIFICATION_ERROR"
                )
            
            # Log activity
            self.log_activity(user["_id"], "verify_email", "user", user["_id"])
            
            return self.create_success_response(
                data={"id": user["_id"], "email": user["email"]},
                message="Email berhasil diverifikasi"
            )
            
        except ValidationException as e:
            return self.create_validation_error_response(e.errors)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memverifikasi email",
                code="EMAIL_VERIFICATION_ERROR"
            )
    
    def forgot_password(self, data: Dict[str, Any]) -> SuccessResponseDTO:
        """Request reset password"""
        try:
            # Validasi input
            forgot_dto = self.validate_dto(UserForgotPasswordDTO, data)
            
            # Find user by email
            user = self.model.find_one({"email": forgot_dto.email})
            if not user:
                # Don't reveal if email exists or not
                return self.create_success_response(
                    data={},
                    message="Jika email terdaftar, link reset password akan dikirim"
                )
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            
            # Update user with reset token
            self.model.update_by_id(user["_id"], {
                "password_reset_token": reset_token,
                "password_reset_expires": datetime.now() + timedelta(hours=1)
            })
            
            # Log activity
            self.log_activity(user["_id"], "forgot_password", "user", user["_id"])
            
            return self.create_success_response(
                data={},
                message="Jika email terdaftar, link reset password akan dikirim",
                meta={"reset_token": reset_token}  # For testing purposes
            )
            
        except ValidationException as e:
            return self.create_validation_error_response(e.errors)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memproses permintaan reset password",
                code="FORGOT_PASSWORD_ERROR"
            )
    
    def reset_password(self, data: Dict[str, Any]) -> SuccessResponseDTO:
        """Reset password dengan token"""
        try:
            # Validasi input
            reset_dto = self.validate_dto(UserResetPasswordDTO, data)
            
            # Find user by token
            user = self.model.find_one({
                "password_reset_token": reset_dto.token,
                "password_reset_expires": {"$gt": datetime.now()}
            })
            
            if not user:
                return self.create_error_response(
                    message="Token reset password tidak valid atau sudah kadaluarsa",
                    code="INVALID_RESET_TOKEN"
                )
            
            # Update password and clear reset token
            success = self.model.update_by_id(user["_id"], {
                "password": self.model.hash_password(reset_dto.new_password),
                "password_reset_token": None,
                "password_reset_expires": None,
                "updated_at": datetime.now()
            })
            
            if not success:
                return self.create_error_response(
                    message="Gagal mereset password",
                    code="RESET_PASSWORD_ERROR"
                )
            
            # Log activity
            self.log_activity(user["_id"], "reset_password", "user", user["_id"])
            
            return self.create_success_response(
                data={"id": user["_id"]},
                message="Password berhasil direset"
            )
            
        except ValidationException as e:
            return self.create_validation_error_response(e.errors)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mereset password",
                code="RESET_PASSWORD_ERROR"
            )
    
    def get_user_list(
        self,
        search_params: Optional[Dict[str, Any]] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None,
        current_user_id: str = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan daftar pengguna (admin only)"""
        try:
            # Check permission
            if current_user_id:
                current_user = self.model.find_by_id(current_user_id)
                if not current_user or current_user.get("role") != "admin":
                    raise PermissionException("view", "user list")
            
            # Validate DTOs
            search_dto = None
            if search_params:
                search_dto = self.validate_dto(UserSearchDTO, search_params)
            
            filter_dto = None
            if filter_params:
                filter_dto = self.validate_dto(UserFilterDTO, filter_params)
            
            pagination_dto = PaginationDTO(**(pagination or {}))
            
            # Build query
            query = {}
            
            # Apply search
            if search_dto and search_dto.query:
                query["$or"] = [
                    {"name": {"$regex": search_dto.query, "$options": "i"}},
                    {"email": {"$regex": search_dto.query, "$options": "i"}}
                ]
            
            # Apply filters
            if filter_dto:
                if filter_dto.role:
                    query["role"] = filter_dto.role
                if filter_dto.is_active is not None:
                    query["is_active"] = filter_dto.is_active
                if filter_dto.is_email_verified is not None:
                    query["is_email_verified"] = filter_dto.is_email_verified
                if filter_dto.created_from:
                    query["created_at"] = {"$gte": filter_dto.created_from}
                if filter_dto.created_to:
                    query.setdefault("created_at", {})["$lte"] = filter_dto.created_to
            
            # Get data with pagination
            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            users = self.model.search_users(
                query=query,
                skip=skip,
                limit=pagination_dto.limit
            )
            
            total = self.model.count_documents(query)
            
            # Convert to response DTOs (remove sensitive data)
            response_data = []
            for user in users:
                user.pop("password", None)
                user.pop("email_verification_token", None)
                user.pop("phone_verification_token", None)
                user.pop("password_reset_token", None)
                response_data.append(UserResponseDTO(**user).dict())
            
            return self.create_paginated_response(
                data=response_data,
                pagination=pagination_dto,
                total=total,
                message="Daftar pengguna berhasil diambil"
            )
            
        except (ValidationException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil daftar pengguna",
                code="USER_LIST_ERROR"
            )
    
    def get_user_stats(self, current_user_id: str) -> SuccessResponseDTO:
        """Mendapatkan statistik pengguna (admin only)"""
        try:
            # Check permission
            current_user = self.model.find_by_id(current_user_id)
            if not current_user or current_user.get("role") != "admin":
                raise PermissionException("view", "user statistics")
            
            stats = self.model.get_user_stats()
            response_data = UserStatsDTO(**stats)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Statistik pengguna berhasil diambil"
            )
            
        except PermissionException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil statistik pengguna",
                code="USER_STATS_ERROR"
            )
    
    def deactivate_user(
        self, 
        user_id: str, 
        current_user_id: str
    ) -> SuccessResponseDTO:
        """Deaktivasi pengguna (admin only)"""
        try:
            # Check permission
            current_user = self.model.find_by_id(current_user_id)
            if not current_user or current_user.get("role") != "admin":
                raise PermissionException("deactivate", "user")
            
            # Check if user exists
            self.check_exists(user_id, "User")
            
            # Deactivate user
            success = self.model.deactivate_user(user_id)
            if not success:
                return self.create_error_response(
                    message="Gagal menonaktifkan pengguna",
                    code="DEACTIVATE_ERROR"
                )
            
            # Log activity
            self.log_activity(current_user_id, "deactivate", "user", user_id)
            
            return self.create_success_response(
                data={"id": user_id},
                message="Pengguna berhasil dinonaktifkan"
            )
            
        except (NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal menonaktifkan pengguna",
                code="DEACTIVATE_ERROR"
            )