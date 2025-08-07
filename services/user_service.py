from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import secrets
from models.user import UserModel
from services.jwt_service import JWTService
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
    UserVerificationDTO,
    UserForgotPasswordDTO,
    UserResetPasswordDTO,
)
from dto.base_dto import PaginationDTO, PaginatedResponseDTO, SuccessResponseDTO
from .base_service import BaseService
from core.exceptions import NotFoundException, DuplicateException, ValidationException, PermissionException

class UserService(BaseService[UserCreateDTO, UserModel]):
    """Service untuk mengelola pengguna"""
    
    def __init__(self):
        super().__init__(UserModel)
        self.jwt_service = JWTService()
    
    def get_resource_name(self) -> str:
        return "User"
    
    def register_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Registrasi pengguna baru"""
        # Data sudah divalidasi di router sebagai UserRegistrationDTO
        # Hapus field yang tidak diperlukan untuk penyimpanan
        sanitized_data = data.copy()
        sanitized_data.pop('confirm_password', None)
        sanitized_data.pop('terms_accepted', None)
        
        # Sanitize input
        sanitized_data = self.sanitize_input(sanitized_data)
        
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
            **sanitized_data,
            "email_verification_token": verification_token,
            "email_verification_expires": datetime.now() + timedelta(hours=24),
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Create user
        user = self.model.create_user(user_data)
        
        # Remove sensitive data and fields not in DTO from response
        user.pop("password", None)
        user.pop("email_verification_token", None)
        user.pop("email_verification_expires", None)
        user.pop("preferences", None)
        user.pop("profile", None)
        user.pop("avatar", None)
        
        # Ensure all required fields for UserResponseDTO exist with proper defaults
        required_fields = {
            'profile_picture': None,
            'address': None,
            'date_of_birth': None,
            'gender': None,
            'occupation': None,
            'last_login': None,
            'is_verified': False,
            'email_verified': False,
            'phone_verified': False,
            'login_count': 0
        }
        
        for field, default_value in required_fields.items():
            if field not in user:
                user[field] = default_value
        
        # Debug: Print user data before DTO conversion
        print(f"User data before DTO conversion: {user}")
        
        # Log activity
        self.log_activity(user["id"], "register", "user", user["id"])
        
        # Convert to response DTO - only include fields that exist in UserResponseDTO
        user_response_data = {
            'id': user.get('id'),
            'name': user.get('name'),
            'email': user.get('email'),
            'phone': user.get('phone'),
            'role': user.get('role'),
            'profile_picture': user.get('profile_picture'),
            'address': user.get('address'),
            'date_of_birth': user.get('date_of_birth'),
            'gender': user.get('gender'),
            'occupation': user.get('occupation'),
            'is_active': user.get('is_active', True),
            'is_verified': user.get('is_verified', False),
            'email_verified': user.get('email_verified', False),
            'phone_verified': user.get('phone_verified', False),
            'last_login': user.get('last_login'),
            'login_count': user.get('login_count', 0),
            'created_at': user.get('created_at'),
            'updated_at': user.get('updated_at')
        }
        
        response_data = UserResponseDTO(**user_response_data)
        
        # Generate JWT tokens for registered user
        access_token = self.jwt_service.create_access_token(user)
        refresh_token = self.jwt_service.create_refresh_token(user)
        
        return {
            "user": response_data.dict(),
            "verification_token": verification_token,
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": self.jwt_service.access_token_expire_minutes * 60,
            "token_type": "Bearer"
        }
    
    def login_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Login pengguna"""
        # Validasi input
        login_dto = self.validate_dto(UserLoginDTO, data)
        
        # Authenticate user
        user = self.model.authenticate_user(login_dto.email, login_dto.password)
        if not user:
            raise ValidationException("Email atau password tidak valid")
        
        # Check if user is active
        if not user.get("is_active", True):
            raise ValidationException("Akun Anda telah dinonaktifkan")
        
        # Store user_id before any modifications
        user_id = user["id"]
        
        # Update last login
        self.model.update_by_id(user_id, {
            "last_login": datetime.now(),
            "login_count": user.get("login_count", 0) + 1
        })
        
        # Prepare user data for DTO (id already converted by base model)
        user_data = user.copy()
        
        # Generate JWT tokens
        access_token = self.jwt_service.create_access_token(user_data)
        refresh_token = self.jwt_service.create_refresh_token(user_data)
        
        # Log activity
        self.log_activity(user_id, "login", "user", user_id)
        
        # Ensure required fields exist with defaults
        user_data.setdefault("is_verified", False)
        user_data.setdefault("created_at", user_data.get("created_at", datetime.now()))
        user_data.setdefault("profile_picture", None)
        
        # Prepare response
        user_profile = UserProfileDTO(**user_data)
        login_response = UserLoginResponseDTO(
            user=user_profile,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=self.jwt_service.access_token_expire_minutes * 60,  # Convert minutes to seconds
            token_type="Bearer"
        )
        
        return login_response.dict()
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token menggunakan refresh token"""
        try:
            # Generate new access token
            new_access_token = self.jwt_service.refresh_access_token(refresh_token)
            
            # Get user data from refresh token
            payload = self.jwt_service.verify_token(refresh_token, "refresh")
            user_id = payload.get("user_id")
            
            # Get updated user data
            user = self.model.find_by_id(user_id)
            if not user:
                raise ValidationException("User tidak ditemukan")
            
            # Check if user is still active
            if not user.get("is_active", True):
                raise ValidationException("Akun telah dinonaktifkan")
            
            # Log activity
            self.log_activity(user_id, "refresh_token", "user", user_id)
            
            return {
                "access_token": new_access_token,
                "expires_in": self.jwt_service.access_token_expire_minutes * 60,
                "token_type": "Bearer"
            }
            
        except ValidationException as e:
            raise e
        except Exception as e:
            raise ValidationException(f"Gagal refresh token: {str(e)}")
    
    def logout_user(self, user_id: str) -> Dict[str, Any]:
        """Logout pengguna (untuk logging purposes)"""
        try:
            # Log activity
            self.log_activity(user_id, "logout", "user", user_id)
            
            return {
                "message": "Logout berhasil"
            }
            
        except Exception as e:
            raise ValidationException(f"Gagal logout: {str(e)}")
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verifikasi JWT token"""
        try:
            payload = self.jwt_service.verify_token(token, "access")
            
            # Get user data
            user_id = payload.get("user_id")
            user = self.model.find_by_id(user_id)
            
            if not user:
                raise ValidationException("User tidak ditemukan")
            
            if not user.get("is_active", True):
                raise ValidationException("Akun telah dinonaktifkan")
            
            # Remove sensitive data
            user.pop("password", None)
            user.pop("email_verification_token", None)
            user.pop("phone_verification_token", None)
            user.pop("password_reset_token", None)
            
            return {
                "valid": True,
                "user": user,
                "payload": payload
            }
            
        except ValidationException as e:
            return {
                "valid": False,
                "error": str(e)
            }
        except Exception as e:
            return {
                "valid": False,
                "error": f"Token verification failed: {str(e)}"
            }
    
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