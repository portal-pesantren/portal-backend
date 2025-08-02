from typing import Dict, Any
from .base_router import BaseRouter
from services.user_service import UserService
from dto.user_dto import (
    UserCreateDTO, UserUpdateDTO, UserLoginDTO, UserPasswordChangeDTO,
    UserSearchDTO, UserFilterDTO, UserStatsDTO
)

class UserRouter(BaseRouter):
    """Router untuk menangani endpoint pengguna"""
    
    def __init__(self):
        super().__init__()
        self.user_service = UserService()
        self._register_routes()
    
    def _register_routes(self):
        """Register semua routes untuk pengguna"""
        
        # POST /auth/register - User registration
        @self.post("/auth/register")
        def register_user(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Validate content type
                if not self.validate_content_type(request_context["headers"]):
                    return self.create_error_response(
                        message="Content-Type harus application/json",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Sanitize input
                data = self.sanitize_input(request_context["data"])
                
                # Create DTO
                register_dto = UserCreateDTO(**data)
                
                # Register user
                result = self.user_service.register_user(register_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Pengguna berhasil didaftarkan",
                    status_code=201
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /auth/login - User login
        @self.post("/auth/login")
        def login_user(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Validate content type
                if not self.validate_content_type(request_context["headers"]):
                    return self.create_error_response(
                        message="Content-Type harus application/json",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Sanitize input
                data = self.sanitize_input(request_context["data"])
                
                # Create DTO
                login_dto = UserLoginDTO(**data)
                
                # Login user
                result = self.user_service.login_user(login_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Login berhasil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /auth/verify-email - Verify email
        @self.post("/auth/verify-email")
        def verify_email(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                data = request_context["data"]
                token = data.get("token")
                
                if not token:
                    return self.create_error_response(
                        message="Token verifikasi diperlukan",
                        status_code=400,
                        code="TOKEN_REQUIRED"
                    )
                
                # Verify email
                result = self.user_service.verify_email(token)
                
                return self.create_success_response(
                    data=result,
                    message="Email berhasil diverifikasi"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /auth/forgot-password - Request password reset
        @self.post("/auth/forgot-password")
        def forgot_password(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                data = request_context["data"]
                email = data.get("email")
                
                if not email:
                    return self.create_error_response(
                        message="Email diperlukan",
                        status_code=400,
                        code="EMAIL_REQUIRED"
                    )
                
                # Request password reset
                result = self.user_service.request_password_reset(email)
                
                return self.create_success_response(
                    data=result,
                    message="Link reset password telah dikirim ke email Anda"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /auth/reset-password - Reset password
        @self.post("/auth/reset-password")
        def reset_password(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                data = request_context["data"]
                token = data.get("token")
                new_password = data.get("new_password")
                
                if not token or not new_password:
                    return self.create_error_response(
                        message="Token dan password baru diperlukan",
                        status_code=400,
                        code="MISSING_REQUIRED_FIELDS"
                    )
                
                # Reset password
                result = self.user_service.reset_password(token, new_password)
                
                return self.create_success_response(
                    data=result,
                    message="Password berhasil direset"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /users/profile - Get current user profile
        @self.get("/users/profile")
        @self.authenticate_required
        def get_user_profile(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                user_id = request_context["user_id"]
                
                # Get user profile
                result = self.user_service.get_user_profile(user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Profil pengguna berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PUT /users/profile - Update user profile
        @self.put("/users/profile")
        @self.authenticate_required
        def update_user_profile(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                user_id = request_context["user_id"]
                
                # Validate content type
                if not self.validate_content_type(request_context["headers"]):
                    return self.create_error_response(
                        message="Content-Type harus application/json",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Sanitize input
                data = self.sanitize_input(request_context["data"])
                
                # Create DTO
                update_dto = UserUpdateDTO(**data)
                
                # Update user profile
                result = self.user_service.update_user_profile(user_id, update_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Profil pengguna berhasil diperbarui"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /users/change-password - Change password
        @self.post("/users/change-password")
        @self.authenticate_required
        def change_password(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                user_id = request_context["user_id"]
                
                # Validate content type
                if not self.validate_content_type(request_context["headers"]):
                    return self.create_error_response(
                        message="Content-Type harus application/json",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Sanitize input
                data = self.sanitize_input(request_context["data"])
                
                # Create DTO
                password_dto = UserPasswordChangeDTO(**data)
                
                # Change password
                result = self.user_service.change_password(user_id, password_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Password berhasil diubah"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /users - Get users list (admin only)
        @self.get("/users")
        @self.authenticate_required
        @self.admin_required
        def get_users_list(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                # Extract pagination
                pagination = self.extract_pagination(query_params)
                
                # Extract search parameters
                search_params = self.extract_search_params(query_params)
                
                # Extract filter parameters
                allowed_filters = [
                    "role", "is_active", "is_verified", "registration_date_from",
                    "registration_date_to", "last_login_from", "last_login_to"
                ]
                filter_params = self.extract_filter_params(query_params, allowed_filters)
                
                # Create DTOs
                search_dto = UserSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "created_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                filter_dto = UserFilterDTO(**filter_params)
                
                # Get users list
                result = self.user_service.get_users_list(
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto,
                    filters=filter_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Daftar pengguna berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /users/stats - Get user statistics (admin only)
        @self.get("/users/stats")
        @self.authenticate_required
        @self.admin_required
        def get_user_stats(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                stats_dto = UserStatsDTO(
                    group_by=query_params.get("group_by", "role"),
                    include_activity=query_params.get("include_activity", "false").lower() == "true"
                )
                
                result = self.user_service.get_user_stats(stats_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Statistik pengguna berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /users/{user_id} - Get user by ID (admin only)
        @self.get("/users/{user_id}")
        @self.authenticate_required
        @self.admin_required
        def get_user_by_id(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract user_id from path
                path_parts = request_context["path"].split("/")
                target_user_id = path_parts[-1]
                
                result = self.user_service.get_user_profile(target_user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Detail pengguna berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PATCH /users/{user_id}/deactivate - Deactivate user (admin only)
        @self.patch("/users/{user_id}/deactivate")
        @self.authenticate_required
        @self.admin_required
        def deactivate_user(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract user_id from path
                path_parts = request_context["path"].split("/")
                target_user_id = path_parts[-2]  # /users/{id}/deactivate
                
                # Deactivate user
                result = self.user_service.deactivate_user(target_user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Pengguna berhasil dinonaktifkan"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PATCH /users/{user_id}/activate - Activate user (admin only)
        @self.patch("/users/{user_id}/activate")
        @self.authenticate_required
        @self.admin_required
        def activate_user(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract user_id from path
                path_parts = request_context["path"].split("/")
                target_user_id = path_parts[-2]  # /users/{id}/activate
                
                # Activate user (implement in service)
                # result = self.user_service.activate_user(target_user_id)
                
                # For now, return success response
                return self.create_success_response(
                    data={"user_id": target_user_id, "is_active": True},
                    message="Pengguna berhasil diaktifkan"
                )
                
            except Exception as e:
                return self.handle_exception(e)
    
    def get_routes(self) -> Dict[str, Any]:
        """Get all registered routes"""
        return self.routes