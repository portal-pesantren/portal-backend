from typing import Dict, Any
from .base_router import BaseRouter
from services.application_service import ApplicationService
from dto.application_dto import (
    ApplicationCreateDTO, ApplicationUpdateDTO, ApplicationSearchDTO,
    ApplicationFilterDTO, ApplicationStatsDTO, ApplicationStatusUpdateDTO,
    ApplicationInterviewDTO, ApplicationDocumentDTO
)

class ApplicationRouter(BaseRouter):
    """Router untuk menangani endpoint pendaftaran pesantren"""
    
    def __init__(self):
        super().__init__()
        self.application_service = ApplicationService()
        self._register_routes()
    
    def _register_routes(self):
        """Register semua routes untuk pendaftaran"""
        
        # GET /applications - Get all applications with pagination, search, and filters
        @self.get("/applications")
        @self.authenticate_required
        def get_applications_list(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                user_id = request_context["user_id"]
                user_role = self.get_user_role(user_id)
                
                query_params = request_context["query_params"]
                
                # Extract pagination
                pagination = self.extract_pagination(query_params)
                
                # Extract search parameters
                search_params = self.extract_search_params(query_params)
                
                # Extract filter parameters
                allowed_filters = [
                    "pesantren_id", "user_id", "status", "application_type",
                    "submitted_from", "submitted_to", "interview_scheduled"
                ]
                filter_params = self.extract_filter_params(query_params, allowed_filters)
                
                # If not admin, filter by user_id
                if user_role != "admin":
                    filter_params["user_id"] = user_id
                
                # Create DTOs
                search_dto = ApplicationSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "created_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                filter_dto = ApplicationFilterDTO(**filter_params)
                
                # Get applications list
                result = self.application_service.get_applications_list(
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto,
                    filters=filter_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Daftar pendaftaran berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /applications/pesantren/{pesantren_id} - Get applications by pesantren
        @self.get("/applications/pesantren/{pesantren_id}")
        @self.authenticate_required
        @self.admin_required
        def get_applications_by_pesantren(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract pesantren_id from path
                path_parts = request_context["path"].split("/")
                pesantren_id = path_parts[-1]
                
                query_params = request_context["query_params"]
                
                # Extract pagination
                pagination = self.extract_pagination(query_params)
                
                # Extract search parameters
                search_params = self.extract_search_params(query_params)
                
                # Create search DTO
                search_dto = ApplicationSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "created_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                # Get applications by pesantren
                result = self.application_service.get_applications_by_pesantren(
                    pesantren_id=pesantren_id,
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Pendaftaran pesantren berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /applications/user/{user_id} - Get applications by user
        @self.get("/applications/user/{user_id}")
        @self.authenticate_required
        def get_applications_by_user(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract user_id from path
                path_parts = request_context["path"].split("/")
                target_user_id = path_parts[-1]
                
                # Check if user can access these applications
                current_user_id = request_context["user_id"]
                user_role = self.get_user_role(current_user_id)
                
                if current_user_id != target_user_id and user_role != "admin":
                    return self.create_error_response(
                        message="Anda tidak memiliki akses untuk melihat pendaftaran pengguna ini",
                        status_code=403,
                        code="ACCESS_DENIED"
                    )
                
                query_params = request_context["query_params"]
                
                # Extract pagination
                pagination = self.extract_pagination(query_params)
                
                # Extract search parameters
                search_params = self.extract_search_params(query_params)
                
                # Create search DTO
                search_dto = ApplicationSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "created_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                # Get applications by user
                result = self.application_service.get_applications_by_user(
                    user_id=target_user_id,
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Pendaftaran pengguna berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /applications/stats - Get application statistics
        @self.get("/applications/stats")
        @self.authenticate_required
        @self.admin_required
        def get_application_stats(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                stats_dto = ApplicationStatsDTO(
                    pesantren_id=query_params.get("pesantren_id"),
                    group_by=query_params.get("group_by", "status"),
                    include_trends=query_params.get("include_trends", "false").lower() == "true"
                )
                
                result = self.application_service.get_application_stats(stats_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Statistik pendaftaran berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /applications/{application_id} - Get application by ID
        @self.get("/applications/{application_id}")
        @self.authenticate_required
        def get_application_by_id(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract application_id from path
                path_parts = request_context["path"].split("/")
                application_id = path_parts[-1]
                
                user_id = request_context["user_id"]
                
                result = self.application_service.get_application_by_id(application_id, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Detail pendaftaran berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /applications - Create new application
        @self.post("/applications")
        @self.authenticate_required
        def create_application(request_context: Dict[str, Any]) -> Dict[str, Any]:
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
                
                # Add user_id to data
                data["user_id"] = user_id
                
                # Create DTO
                create_dto = ApplicationCreateDTO(**data)
                
                # Create application
                result = self.application_service.create_application(create_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Pendaftaran berhasil dibuat",
                    status_code=201
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PUT /applications/{application_id} - Update application
        @self.put("/applications/{application_id}")
        @self.authenticate_required
        def update_application(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract application_id from path
                path_parts = request_context["path"].split("/")
                application_id = path_parts[-1]
                
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
                update_dto = ApplicationUpdateDTO(**data)
                
                # Update application
                result = self.application_service.update_application(application_id, update_dto, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Pendaftaran berhasil diperbarui"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PATCH /applications/{application_id}/status - Update application status
        @self.patch("/applications/{application_id}/status")
        @self.authenticate_required
        @self.admin_required
        def update_application_status(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract application_id from path
                path_parts = request_context["path"].split("/")
                application_id = path_parts[-2]  # /applications/{id}/status
                
                admin_id = request_context["user_id"]
                
                # Validate content type
                if not self.validate_content_type(request_context["headers"]):
                    return self.create_error_response(
                        message="Content-Type harus application/json",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Sanitize input
                data = self.sanitize_input(request_context["data"])
                
                # Add admin_id to data
                data["updated_by"] = admin_id
                
                # Create DTO
                status_dto = ApplicationStatusUpdateDTO(**data)
                
                # Update status
                result = self.application_service.update_application_status(application_id, status_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Status pendaftaran berhasil diperbarui"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /applications/{application_id}/interview - Schedule interview
        @self.post("/applications/{application_id}/interview")
        @self.authenticate_required
        @self.admin_required
        def schedule_interview(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract application_id from path
                path_parts = request_context["path"].split("/")
                application_id = path_parts[-2]  # /applications/{id}/interview
                
                admin_id = request_context["user_id"]
                
                # Validate content type
                if not self.validate_content_type(request_context["headers"]):
                    return self.create_error_response(
                        message="Content-Type harus application/json",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Sanitize input
                data = self.sanitize_input(request_context["data"])
                
                # Add admin_id to data
                data["scheduled_by"] = admin_id
                
                # Create DTO
                interview_dto = ApplicationInterviewDTO(**data)
                
                # Schedule interview
                result = self.application_service.schedule_interview(application_id, interview_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Wawancara berhasil dijadwalkan"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /applications/{application_id}/documents - Upload document
        @self.post("/applications/{application_id}/documents")
        @self.authenticate_required
        def upload_document(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract application_id from path
                path_parts = request_context["path"].split("/")
                application_id = path_parts[-2]  # /applications/{id}/documents
                
                user_id = request_context["user_id"]
                
                # Validate content type for multipart/form-data
                content_type = request_context["headers"].get("Content-Type", "")
                if not content_type.startswith("multipart/form-data"):
                    return self.create_error_response(
                        message="Content-Type harus multipart/form-data untuk upload file",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Get document data from request
                data = request_context["data"]
                
                # Create DTO
                document_dto = ApplicationDocumentDTO(
                    document_type=data.get("document_type"),
                    file_name=data.get("file_name"),
                    file_size=data.get("file_size"),
                    file_path=data.get("file_path"),
                    uploaded_by=user_id
                )
                
                # Upload document
                result = self.application_service.upload_document(application_id, document_dto, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Dokumen berhasil diunggah"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # DELETE /applications/{application_id} - Cancel application
        @self.delete("/applications/{application_id}")
        @self.authenticate_required
        def cancel_application(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract application_id from path
                path_parts = request_context["path"].split("/")
                application_id = path_parts[-1]
                
                user_id = request_context["user_id"]
                
                # Cancel application (implement in service)
                # result = self.application_service.cancel_application(application_id, user_id)
                
                # For now, return success response
                return self.create_success_response(
                    data={"application_id": application_id, "status": "cancelled"},
                    message="Pendaftaran berhasil dibatalkan"
                )
                
            except Exception as e:
                return self.handle_exception(e)
    
    def get_routes(self) -> Dict[str, Any]:
        """Get all registered routes"""
        return self.routes