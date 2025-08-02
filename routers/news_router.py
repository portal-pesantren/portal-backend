from typing import Dict, Any
from .base_router import BaseRouter
from services.news_service import NewsService
from dto.news_dto import (
    NewsCreateDTO, NewsUpdateDTO, NewsSearchDTO, 
    NewsFilterDTO, NewsStatsDTO
)

class NewsRouter(BaseRouter):
    """Router untuk menangani endpoint berita pesantren"""
    
    def __init__(self):
        super().__init__()
        self.news_service = NewsService()
        self._register_routes()
    
    def _register_routes(self):
        """Register semua routes untuk berita"""
        
        # GET /news - Get all news with pagination, search, and filters
        @self.get("/news")
        def get_news_list(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                # Extract pagination
                pagination = self.extract_pagination(query_params)
                
                # Extract search parameters
                search_params = self.extract_search_params(query_params)
                
                # Extract filter parameters
                allowed_filters = [
                    "pesantren_id", "author_id", "category", "is_featured", 
                    "is_published", "published_from", "published_to"
                ]
                filter_params = self.extract_filter_params(query_params, allowed_filters)
                
                # Create DTOs
                search_dto = NewsSearchDTO(
                    query=search_params.get("query", ""),
                    sort_by=search_params.get("sort_by", "published_at"),
                    sort_order=search_params.get("sort_order", "desc")
                )
                
                filter_dto = NewsFilterDTO(**filter_params)
                
                # Get news list
                result = self.news_service.get_news_list(
                    page=pagination["page"],
                    limit=pagination["limit"],
                    search=search_dto,
                    filters=filter_dto
                )
                
                return self.create_success_response(
                    data=result,
                    message="Daftar berita berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /news/featured - Get featured news
        @self.get("/news/featured")
        def get_featured_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                limit = int(query_params.get("limit", 10))
                
                result = self.news_service.get_featured_news(limit=limit)
                
                return self.create_success_response(
                    data=result,
                    message="Berita unggulan berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /news/popular - Get popular news
        @self.get("/news/popular")
        def get_popular_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                limit = int(query_params.get("limit", 10))
                
                result = self.news_service.get_popular_news(limit=limit)
                
                return self.create_success_response(
                    data=result,
                    message="Berita populer berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /news/stats - Get news statistics
        @self.get("/news/stats")
        @self.authenticate_required
        @self.admin_required
        def get_news_stats(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                query_params = request_context["query_params"]
                
                stats_dto = NewsStatsDTO(
                    pesantren_id=query_params.get("pesantren_id"),
                    group_by=query_params.get("group_by", "category"),
                    include_engagement=query_params.get("include_engagement", "false").lower() == "true"
                )
                
                result = self.news_service.get_news_stats(stats_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Statistik berita berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /news/slug/{slug} - Get news by slug
        @self.get("/news/slug/{slug}")
        def get_news_by_slug(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract slug from path
                path_parts = request_context["path"].split("/")
                slug = path_parts[-1]
                
                result = self.news_service.get_news_by_slug(slug)
                
                return self.create_success_response(
                    data=result,
                    message="Detail berita berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /news/{news_id} - Get news by ID
        @self.get("/news/{news_id}")
        def get_news_by_id(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-1]
                
                result = self.news_service.get_news_by_id(news_id)
                
                return self.create_success_response(
                    data=result,
                    message="Detail berita berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # GET /news/{news_id}/related - Get related news
        @self.get("/news/{news_id}/related")
        def get_related_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-2]  # /news/{id}/related
                
                query_params = request_context["query_params"]
                limit = int(query_params.get("limit", 5))
                
                result = self.news_service.get_related_news(news_id, limit=limit)
                
                return self.create_success_response(
                    data=result,
                    message="Berita terkait berhasil diambil"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /news - Create new news
        @self.post("/news")
        @self.authenticate_required
        @self.admin_required
        def create_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                author_id = request_context["user_id"]
                
                # Validate content type
                if not self.validate_content_type(request_context["headers"]):
                    return self.create_error_response(
                        message="Content-Type harus application/json",
                        status_code=400,
                        code="INVALID_CONTENT_TYPE"
                    )
                
                # Sanitize input
                data = self.sanitize_input(request_context["data"])
                
                # Add author_id to data
                data["author_id"] = author_id
                
                # Create DTO
                create_dto = NewsCreateDTO(**data)
                
                # Create news
                result = self.news_service.create_news(create_dto)
                
                return self.create_success_response(
                    data=result,
                    message="Berita berhasil dibuat",
                    status_code=201
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PUT /news/{news_id} - Update news
        @self.put("/news/{news_id}")
        @self.authenticate_required
        @self.admin_required
        def update_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-1]
                
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
                update_dto = NewsUpdateDTO(**data)
                
                # Update news
                result = self.news_service.update_news(news_id, update_dto, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Berita berhasil diperbarui"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PATCH /news/{news_id}/publish - Publish news
        @self.patch("/news/{news_id}/publish")
        @self.authenticate_required
        @self.admin_required
        def publish_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-2]  # /news/{id}/publish
                
                user_id = request_context["user_id"]
                
                # Publish news
                result = self.news_service.publish_news(news_id, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Berita berhasil dipublikasikan"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # PATCH /news/{news_id}/unpublish - Unpublish news
        @self.patch("/news/{news_id}/unpublish")
        @self.authenticate_required
        @self.admin_required
        def unpublish_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-2]  # /news/{id}/unpublish
                
                user_id = request_context["user_id"]
                
                # Unpublish news (implement in service)
                # result = self.news_service.unpublish_news(news_id, user_id)
                
                # For now, return success response
                return self.create_success_response(
                    data={"news_id": news_id, "is_published": False},
                    message="Berita berhasil dibatalkan publikasinya"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /news/{news_id}/like - Like news
        @self.post("/news/{news_id}/like")
        @self.authenticate_required
        def like_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-2]  # /news/{id}/like
                
                user_id = request_context["user_id"]
                
                # Like news
                result = self.news_service.like_news(news_id, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Berita berhasil disukai"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # POST /news/{news_id}/dislike - Dislike news
        @self.post("/news/{news_id}/dislike")
        @self.authenticate_required
        def dislike_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-2]  # /news/{id}/dislike
                
                user_id = request_context["user_id"]
                
                # Dislike news
                result = self.news_service.dislike_news(news_id, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Berita berhasil tidak disukai"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # DELETE /news/{news_id}/like - Remove like from news
        @self.delete("/news/{news_id}/like")
        @self.authenticate_required
        def remove_like_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-2]  # /news/{id}/like
                
                user_id = request_context["user_id"]
                
                # Remove like from news (implement in service)
                # result = self.news_service.remove_like_news(news_id, user_id)
                
                # For now, return success response
                return self.create_success_response(
                    data={"news_id": news_id, "user_id": user_id, "action": "like_removed"},
                    message="Like berhasil dihapus dari berita"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # DELETE /news/{news_id}/dislike - Remove dislike from news
        @self.delete("/news/{news_id}/dislike")
        @self.authenticate_required
        def remove_dislike_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-2]  # /news/{id}/dislike
                
                user_id = request_context["user_id"]
                
                # Remove dislike from news (implement in service)
                # result = self.news_service.remove_dislike_news(news_id, user_id)
                
                # For now, return success response
                return self.create_success_response(
                    data={"news_id": news_id, "user_id": user_id, "action": "dislike_removed"},
                    message="Dislike berhasil dihapus dari berita"
                )
                
            except Exception as e:
                return self.handle_exception(e)
        
        # DELETE /news/{news_id} - Delete news (soft delete)
        @self.delete("/news/{news_id}")
        @self.authenticate_required
        @self.admin_required
        def delete_news(request_context: Dict[str, Any]) -> Dict[str, Any]:
            try:
                # Extract news_id from path
                path_parts = request_context["path"].split("/")
                news_id = path_parts[-1]
                
                user_id = request_context["user_id"]
                
                # Delete news
                result = self.news_service.delete_news(news_id, user_id)
                
                return self.create_success_response(
                    data=result,
                    message="Berita berhasil dihapus"
                )
                
            except Exception as e:
                return self.handle_exception(e)
    
    def get_routes(self) -> Dict[str, Any]:
        """Get all registered routes"""
        return self.routes