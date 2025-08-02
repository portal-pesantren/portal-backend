from typing import Dict, Any
from .base_router import BaseRouter
from services.consultation_service import ConsultationService
from dto.consultation_dto import (
    ConsultationCreateDTO, ConsultationUpdateDTO, ConsultationResponseDTO,
    ConsultationSearchDTO, ConsultationFilterDTO, ConsultationStatsDTO,
    ConsultationRatingDTO
)

class ConsultationRouter(BaseRouter):
    """Router untuk menangani endpoint konsultasi pesantren"""
    
    def __init__(self):
        super().__init__()
        self.consultation_service = ConsultationService()
        self._register_routes()
    
    def _register_routes(self):
        """Register semua routes untuk konsultasi"""
        
        # GET /consultations - Get all consultations with pagination, search, and filters
        @self.get("/consultations")
        @self.authenticate_required
        def get_consultations_list(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                user_id = request_context["user_id"]
                user_role = request_context.get("user_role", "user")
                
                # Extract pagination
                pagination = self.extract_pagination(query_params)
                
                # Extract search parameters
                search_params = self.extract_search_params(query_params)
                
                # Extract filter parameters
                allowed_filters = [
                    "pesantren_id", "consultant_id", "status", "priority", 
                    "category", "created_from", "created_to", "is_urgent"
                ]
                filter_params = self.extract_filter_params(query_params, allowed_filters)
                
                # Add user filter for non-admin users
                if user_role != "admin":
                    filter_params["user_id"] = user_id
                
                # Create DTOs
                search_dto = ConsultationSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "created_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                filter_dto = ConsultationFilterDTO(**filter_params)
                
                # Get consultations list
                result = self.consultation_service.get_consultations_list(
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto,
                    filters=filter_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Daftar konsultasi berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /consultations/stats - Get consultation statistics
        @self.get("/consultations/stats")
        @self.authenticate_required
        @self.admin_required
        def get_consultation_stats(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                stats_dto = ConsultationStatsDTO(
                    pesantren_id=query_params.get("pesantren_id"),
                    consultant_id=query_params.get("consultant_id"),
                    group_by=query_params.get("group_by", "status"),
                    include_ratings=query_params.get("include_ratings", "false").lower() == "true",
                    date_from=query_params.get("date_from"),
                    date_to=query_params.get("date_to")
                )
                
                result = self.consultation_service.get_consultation_stats(stats_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Statistik konsultasi berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /consultations/analytics - Get consultation analytics
        @self.get("/consultations/analytics")
        @self.authenticate_required
        @self.admin_required
        def get_consultation_analytics(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                period = query_params.get("period", "month")
                pesantren_id = query_params.get("pesantren_id")
                
                result = self.consultation_service.get_consultation_analytics(
                    period=period,
                    pesantren_id=pesantren_id
                )
                
                return self.create_success_response(
                    data=result,
                    message="Analitik konsultasi berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /consultations/{consultation_id} - Get consultation by ID
        @self.get("/consultations/{consultation_id}")
        @self.authenticate_required
        def get_consultation_by_id(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract consultation_id from path
                path_parts = request_context["path"].split("/")
                consultation_id = path_parts[-1]
                
                user_id = request_context["user_id"]
                user_role = request_context.get("user_role", "user")
                
                result = self.consultation_service.get_consultation_by_id(
                    consultation_id, 
                    user_id=user_id if user_role != "admin" else None
                )
                
                return self.create_success_response(
                    data=result,
                    message="Detail konsultasi berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /consultations - Create new consultation
        @self.post("/consultations")
        @self.authenticate_required
        def create_consultation(request_context: Dict[str, Any]) -> Dict[str, Any]:
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
                create_dto = ConsultationCreateDTO(**data)
                
                # Create consultation
                result = self.consultation_service.create_consultation(create_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Konsultasi berhasil dibuat",
                    status_code=201
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PUT /consultations/{consultation_id} - Update consultation
        @self.put("/consultations/{consultation_id}")
        @self.authenticate_required
        def update_consultation(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract consultation_id from path
                path_parts = request_context["path"].split("/")
                consultation_id = path_parts[-1]
                
                user_id = request_context["user_id"]
                user_role = request_context.get("user_role", "user")
                
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
                update_dto = ConsultationUpdateDTO(**data)
                
                # Update consultation
                result = self.consultation_service.update_consultation(
                    consultation_id, 
                    update_dto, 
                    user_id=user_id if user_role != "admin" else None
                )
                
                return self.create_success_response(
                    data=result,
                    message="Konsultasi berhasil diperbarui"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /consultations/{consultation_id}/responses - Create consultation response
        @self.post("/consultations/{consultation_id}/responses")
        @self.authenticate_required
        def create_consultation_response(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract consultation_id from path
                path_parts = request_context["path"].split("/")
                consultation_id = path_parts[-2]  # /consultations/{id}/responses
                
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
                
                # Add responder_id to data
                data["responder_id"] = user_id
                data["consultation_id"] = consultation_id
                
                # Create DTO
                response_dto = ConsultationResponseDTO(**data)
                
                # Create response
                result = self.consultation_service.create_consultation_response(
                    consultation_id, 
                    response_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Respons konsultasi berhasil dibuat",
                    status_code=201
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PATCH /consultations/{consultation_id}/assign - Assign consultant
        @self.patch("/consultations/{consultation_id}/assign")
        @self.authenticate_required
        @self.admin_required
        def assign_consultant(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract consultation_id from path
                path_parts = request_context["path"].split("/")
                consultation_id = path_parts[-2]  # /consultations/{id}/assign
                
                # Validate content type
                if not self.validate_content_type(request_context["headers"]):
                    return self.create_error_response(
                        message="Content-Type harus application/json",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Sanitize input
                data = self.sanitize_input(request_context["data"])
                consultant_id = data.get("consultant_id")
                
                if not consultant_id:
                    return self.create_error_response(
                        message="consultant_id diperlukan",
                        status_code=400,
                        code="MISSING_CONSULTANT_ID"
                    )
                
                # Assign consultant
                result = self.consultation_service.assign_consultant(
                    consultation_id, 
                    consultant_id
                )
                
                return self.create_success_response(
                    data=result,
                    message="Konsultan berhasil ditugaskan"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PATCH /consultations/{consultation_id}/status - Update consultation status
        @self.patch("/consultations/{consultation_id}/status")
        @self.authenticate_required
        def update_consultation_status(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract consultation_id from path
                path_parts = request_context["path"].split("/")
                consultation_id = path_parts[-2]  # /consultations/{id}/status
                
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
                status = data.get("status")
                
                if not status:
                    return self.create_error_response(
                        message="status diperlukan",
                        status_code=400,
                        code="MISSING_STATUS"
                    )
                
                # Update status
                result = self.consultation_service.update_consultation_status(
                    consultation_id, 
                    status, 
                    user_id
                )
                
                return self.create_success_response(
                    data=result,
                    message="Status konsultasi berhasil diperbarui"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /consultations/{consultation_id}/rating - Rate consultation
        @self.post("/consultations/{consultation_id}/rating")
        @self.authenticate_required
        def rate_consultation(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract consultation_id from path
                path_parts = request_context["path"].split("/")
                consultation_id = path_parts[-2]  # /consultations/{id}/rating
                
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
                
                # Add user_id and consultation_id to data
                data["user_id"] = user_id
                data["consultation_id"] = consultation_id
                
                # Create DTO
                rating_dto = ConsultationRatingDTO(**data)
                
                # Rate consultation
                result = self.consultation_service.rate_consultation(
                    consultation_id, 
                    rating_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Rating konsultasi berhasil diberikan",
                    status_code=201
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # DELETE /consultations/{consultation_id} - Delete consultation (soft delete)
        @self.delete("/consultations/{consultation_id}")
        @self.authenticate_required
        def delete_consultation(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract consultation_id from path
                path_parts = request_context["path"].split("/")
                consultation_id = path_parts[-1]
                
                user_id = request_context["user_id"]
                user_role = request_context.get("user_role", "user")
                
                # Delete consultation
                result = self.consultation_service.delete_consultation(
                    consultation_id, 
                    user_id=user_id if user_role != "admin" else None
                )
                
                return self.create_success_response(
                    data=result,
                    message="Konsultasi berhasil dihapus"
                )
                
            except Exception as e:
                return self.handle_exception(e)
    
    def get_routes(self) -> Dict[str, Any]:
        """Get all registered routes"""
        return self.routes