from typing import Dict, Any
from .base_router import BaseRouter
from services.pesantren_service import PesantrenService
from dto.pesantren_dto import (
    PesantrenCreateDTO, PesantrenUpdateDTO, PesantrenSearchDTO, 
    PesantrenFilterDTO, PesantrenStatsDTO
)

class PesantrenRouter(BaseRouter):
    """Router untuk menangani endpoint pesantren"""
    
    def __init__(self):
        super().__init__()
        self.pesantren_service = PesantrenService()
        self._register_routes()
    
    def _register_routes(self):
        """Register semua routes untuk pesantren"""
        
        # GET /pesantren - Get all pesantren with pagination, search, and filters
        @self.get("/pesantren")
        def get_pesantren_list(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                # Extract pagination
                pagination = self.extract_pagination(query_params)
                
                # Extract search parameters
                search_params = self.extract_search_params(query_params)
                
                # Extract filter parameters
                allowed_filters = [
                    "province", "city", "type", "is_featured", "status",
                    "min_capacity", "max_capacity", "has_scholarship"
                ]
                filter_params = self.extract_filter_params(query_params, allowed_filters)
                
                # Create DTOs
                search_dto = PesantrenSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "created_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                filter_dto = PesantrenFilterDTO(**filter_params)
                
                # Get pesantren list
                result = self.pesantren_service.get_pesantren_list(
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto,
                    filters=filter_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Daftar pesantren berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /pesantren/featured - Get featured pesantren
        @self.get("/pesantren/featured")
        def get_featured_pesantren(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                limit = int(query_params.get("limit", 10))
                
                result = self.pesantren_service.get_featured_pesantren(limit=limit)
                
                return self.create_success_response(
                    data=result,
                    message="Pesantren unggulan berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /pesantren/popular - Get popular pesantren
        @self.get("/pesantren/popular")
        def get_popular_pesantren(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                limit = int(query_params.get("limit", 10))
                
                result = self.pesantren_service.get_popular_pesantren(limit=limit)
                
                return self.create_success_response(
                    data=result,
                    message="Pesantren populer berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /pesantren/stats - Get pesantren statistics
        @self.get("/pesantren/stats")
        def get_pesantren_stats(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                stats_dto = PesantrenStatsDTO(
                    group_by=query_params.get("group_by", "province"),
                    include_programs=query_params.get("include_programs", "false").lower() == "true"
                )
                
                result = self.pesantren_service.get_pesantren_stats(stats_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Statistik pesantren berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /pesantren/{pesantren_id} - Get pesantren by ID
        @self.get("/pesantren/{pesantren_id}")
        def get_pesantren_by_id(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract pesantren_id from path
                path_parts = request_context["path"].split("/")
                pesantren_id = path_parts[-1]
                
                result = self.pesantren_service.get_pesantren_by_id(pesantren_id)
                
                return self.create_success_response(
                    data=result,
                    message="Detail pesantren berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /pesantren - Create new pesantren
        @self.post("/pesantren")
        @self.authenticate_required
        @self.admin_required
        def create_pesantren(request_context: Dict[str, Any]) -> Dict[str, Any]:
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
                create_dto = PesantrenCreateDTO(**data)
                
                # Create pesantren
                result = self.pesantren_service.create_pesantren(create_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Pesantren berhasil dibuat",
                    status_code=201
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PUT /pesantren/{pesantren_id} - Update pesantren
        @self.put("/pesantren/{pesantren_id}")
        @self.authenticate_required
        @self.admin_required
        def update_pesantren(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract pesantren_id from path
                path_parts = request_context["path"].split("/")
                pesantren_id = path_parts[-1]
                
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
                update_dto = PesantrenUpdateDTO(**data)
                
                # Update pesantren
                result = self.pesantren_service.update_pesantren(pesantren_id, update_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Pesantren berhasil diperbarui"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PATCH /pesantren/{pesantren_id}/featured - Set featured status
        @self.patch("/pesantren/{pesantren_id}/featured")
        @self.authenticate_required
        @self.admin_required
        def set_featured_status(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract pesantren_id from path
                path_parts = request_context["path"].split("/")
                pesantren_id = path_parts[-3]  # /pesantren/{id}/featured
                
                # Get featured status from request body
                data = request_context["data"]
                is_featured = data.get("is_featured", False)
                
                # Set featured status
                result = self.pesantren_service.set_featured_status(pesantren_id, is_featured)
                
                status_text = "unggulan" if is_featured else "tidak unggulan"
                return self.create_success_response(
                    data=result,
                    message=f"Status pesantren berhasil diubah menjadi {status_text}"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # DELETE /pesantren/{pesantren_id} - Delete pesantren (soft delete)
        @self.delete("/pesantren/{pesantren_id}")
        @self.authenticate_required
        @self.admin_required
        def delete_pesantren(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract pesantren_id from path
                path_parts = request_context["path"].split("/")
                pesantren_id = path_parts[-1]
                
                # Delete pesantren
                result = self.pesantren_service.delete_pesantren(pesantren_id)
                
                return self.create_success_response(
                    data=result,
                    message="Pesantren berhasil dihapus"
                )
                
            except Exception as e:
                return self.handle_exception(e)
    
    def get_routes(self) -> Dict[str, Any]:
        """Get all registered routes"""
        return self.routes
    
    def get_all_routes(self) -> list:
        """
        Get all registered routes for Pesantren router
        """
        return [
            {"method": "GET", "path": "/pesantren", "handler": "get_pesantren_list"},
            {"method": "GET", "path": "/pesantren/featured", "handler": "get_featured_pesantren"},
            {"method": "GET", "path": "/pesantren/popular", "handler": "get_popular_pesantren"},
            {"method": "GET", "path": "/pesantren/stats", "handler": "get_pesantren_stats"},
            {"method": "GET", "path": "/pesantren/{pesantren_id}", "handler": "get_pesantren_by_id"},
            {"method": "POST", "path": "/pesantren", "handler": "create_pesantren"},
            {"method": "PUT", "path": "/pesantren/{pesantren_id}", "handler": "update_pesantren"},
            {"method": "PATCH", "path": "/pesantren/{pesantren_id}/featured", "handler": "set_featured_status"},
            {"method": "DELETE", "path": "/pesantren/{pesantren_id}", "handler": "delete_pesantren"}
        ]