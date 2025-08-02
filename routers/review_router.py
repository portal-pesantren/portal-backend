from typing import Dict, Any
from .base_router import BaseRouter
from services.review_service import ReviewService
from dto.review_dto import (
    ReviewCreateDTO, ReviewUpdateDTO, ReviewSearchDTO, 
    ReviewFilterDTO, ReviewStatsDTO, ReviewModerationDTO
)

class ReviewRouter(BaseRouter):
    """Router untuk menangani endpoint ulasan pesantren"""
    
    def __init__(self):
        super().__init__()
        self.review_service = ReviewService()
        self._register_routes()
    
    def _register_routes(self):
        """Register semua routes untuk ulasan"""
        
        # GET /reviews - Get all reviews with pagination, search, and filters
        @self.get("/reviews")
        def get_reviews_list(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                # Extract pagination
                pagination = self.extract_pagination(query_params)
                
                # Extract search parameters
                search_params = self.extract_search_params(query_params)
                
                # Extract filter parameters
                allowed_filters = [
                    "pesantren_id", "user_id", "rating", "min_rating", "max_rating",
                    "is_verified", "status", "created_from", "created_to"
                ]
                filter_params = self.extract_filter_params(query_params, allowed_filters)
                
                # Create DTOs
                search_dto = ReviewSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "created_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                filter_dto = ReviewFilterDTO(**filter_params)
                
                # Get reviews list
                result = self.review_service.get_reviews_list(
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto,
                    filters=filter_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Daftar ulasan berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /reviews/pesantren/{pesantren_id} - Get reviews by pesantren
        @self.get("/reviews/pesantren/{pesantren_id}")
        def get_reviews_by_pesantren(request_context: Dict[str, Any]) -> Dict[str, Any]:
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
                search_dto = ReviewSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "created_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                # Get reviews by pesantren
                result = self.review_service.get_reviews_by_pesantren(
                    pesantren_id=pesantren_id,
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Ulasan pesantren berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /reviews/user/{user_id} - Get reviews by user
        @self.get("/reviews/user/{user_id}")
        @self.authenticate_required
        def get_reviews_by_user(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract user_id from path
                path_parts = request_context["path"].split("/")
                target_user_id = path_parts[-1]
                
                # Check if user can access these reviews
                current_user_id = request_context["user_id"]
                user_role = self.get_user_role(current_user_id)
                
                if current_user_id != target_user_id and user_role != "admin":
                    return self.create_error_response(
                        message="Anda tidak memiliki akses untuk melihat ulasan pengguna ini",
                        status_code=403,
                        code="ACCESS_DENIED"
                    )
                
                query_params = request_context["query_params"]
                
                # Extract pagination
                pagination = self.extract_pagination(query_params)
                
                # Extract search parameters
                search_params = self.extract_search_params(query_params)
                
                # Create search DTO
                search_dto = ReviewSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "created_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                # Get reviews by user
                result = self.review_service.get_reviews_by_user(
                    user_id=target_user_id,
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Ulasan pengguna berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /reviews/stats - Get review statistics
        @self.get("/reviews/stats")
        def get_review_stats(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                stats_dto = ReviewStatsDTO(
                    pesantren_id=query_params.get("pesantren_id"),
                    group_by=query_params.get("group_by", "rating"),
                    include_trends=query_params.get("include_trends", "false").lower() == "true"
                )
                
                result = self.review_service.get_review_stats(stats_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Statistik ulasan berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /reviews/{review_id} - Get review by ID
        @self.get("/reviews/{review_id}")
        def get_review_by_id(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract review_id from path
                path_parts = request_context["path"].split("/")
                review_id = path_parts[-1]
                
                result = self.review_service.get_review_by_id(review_id)
                
                return self.create_success_response(
                    data=result,
                    message="Detail ulasan berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /reviews - Create new review
        @self.post("/reviews")
        @self.authenticate_required
        def create_review(request_context: Dict[str, Any]) -> Dict[str, Any]:
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
                create_dto = ReviewCreateDTO(**data)
                
                # Create review
                result = self.review_service.create_review(create_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Ulasan berhasil dibuat",
                    status_code=201
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PUT /reviews/{review_id} - Update review
        @self.put("/reviews/{review_id}")
        @self.authenticate_required
        def update_review(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract review_id from path
                path_parts = request_context["path"].split("/")
                review_id = path_parts[-1]
                
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
                update_dto = ReviewUpdateDTO(**data)
                
                # Update review
                result = self.review_service.update_review(review_id, update_dto, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Ulasan berhasil diperbarui"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /reviews/{review_id}/helpful - Mark review as helpful
        @self.post("/reviews/{review_id}/helpful")
        @self.authenticate_required
        def mark_helpful(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract review_id from path
                path_parts = request_context["path"].split("/")
                review_id = path_parts[-2]  # /reviews/{id}/helpful
                
                user_id = request_context["user_id"]
                
                # Mark as helpful
                result = self.review_service.mark_helpful(review_id, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Ulasan berhasil ditandai sebagai bermanfaat"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /reviews/{review_id}/report - Report review
        @self.post("/reviews/{review_id}/report")
        @self.authenticate_required
        def report_review(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract review_id from path
                path_parts = request_context["path"].split("/")
                review_id = path_parts[-2]  # /reviews/{id}/report
                
                user_id = request_context["user_id"]
                
                # Get report reason from request body
                data = request_context["data"]
                reason = data.get("reason", "Konten tidak pantas")
                
                # Report review
                result = self.review_service.report_review(review_id, user_id, reason)
                
                return self.create_success_response(
                    data=result,
                    message="Ulasan berhasil dilaporkan"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /reviews/{review_id}/moderate - Moderate review (admin only)
        @self.post("/reviews/{review_id}/moderate")
        @self.authenticate_required
        @self.admin_required
        def moderate_review(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract review_id from path
                path_parts = request_context["path"].split("/")
                review_id = path_parts[-2]  # /reviews/{id}/moderate
                
                moderator_id = request_context["user_id"]
                
                # Validate content type
                if not self.validate_content_type(request_context["headers"]):
                    return self.create_error_response(
                        message="Content-Type harus application/json",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Sanitize input
                data = self.sanitize_input(request_context["data"])
                
                # Add moderator_id to data
                data["moderator_id"] = moderator_id
                
                # Create DTO
                moderation_dto = ReviewModerationDTO(**data)
                
                # Moderate review
                result = self.review_service.moderate_review(review_id, moderation_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Ulasan berhasil dimoderasi"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # DELETE /reviews/{review_id} - Delete review (soft delete)
        @self.delete("/reviews/{review_id}")
        @self.authenticate_required
        def delete_review(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract review_id from path
                path_parts = request_context["path"].split("/")
                review_id = path_parts[-1]
                
                user_id = request_context["user_id"]
                
                # Delete review
                result = self.review_service.delete_review(review_id, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Ulasan berhasil dihapus"
                )
                
            except Exception as e:
                return self.handle_exception(e)
    
    def get_routes(self) -> Dict[str, Any]:
        """Get all registered routes"""
        return self.routes