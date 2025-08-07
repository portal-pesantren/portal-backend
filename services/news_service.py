from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import secrets
from models.news import NewsModel
from models.user import UserModel
from dto.news_dto import (
    NewsCreateDTO,
    NewsUpdateDTO,
    NewsResponseDTO,
    NewsSummaryDTO,
    NewsSearchDTO,
    NewsFilterDTO,
    NewsStatsDTO,
    NewsLikeDTO,
    NewsPublishDTO,
    NewsAnalyticsDTO,
    NewsBulkActionDTO,
    NewsRelatedDTO,
    NewsSEODTO
)
from dto.base_dto import PaginationDTO, PaginatedResponseDTO, SuccessResponseDTO
from .base_service import BaseService
from core.exceptions import NotFoundException, DuplicateException, ValidationException, PermissionException

class NewsService(BaseService[NewsCreateDTO, NewsModel]):
    """Service untuk mengelola berita pesantren"""
    
    def __init__(self):
        super().__init__(NewsModel)
        self.user_model = UserModel()
    
    def get_resource_name(self) -> str:
        return "News"
    
    def create_news(self, data: Dict[str, Any], author_id: str) -> SuccessResponseDTO:
        """Membuat berita baru"""
        try:
            # Check permission
            author = self.user_model.find_by_id(author_id)
            if not author or author.get("role") not in ["admin", "editor", "pesantren_admin"]:
                raise PermissionException("create", "news")
            
            # Validasi input
            news_dto = self.validate_dto(NewsCreateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(news_dto.dict())
            
            # Check duplicate slug
            if sanitized_data.get("slug"):
                existing_slug = self.model.find_one({"slug": sanitized_data["slug"]})
                if existing_slug:
                    raise DuplicateException("News", "slug", sanitized_data["slug"])
            else:
                # Generate slug from title
                sanitized_data["slug"] = self._generate_slug(sanitized_data["title"])
            
            # Prepare news data
            news_data = {
                "title": sanitized_data["title"],
                "slug": sanitized_data["slug"],
                "content": sanitized_data["content"],
                "excerpt": sanitized_data.get("excerpt") or self._generate_excerpt(sanitized_data["content"]),
                "featured_image": sanitized_data.get("featured_image"),
                "category": sanitized_data["category"],
                "tags": sanitized_data.get("tags", []),
                "author_id": author_id,
                "status": sanitized_data.get("status", "draft"),
                "is_featured": sanitized_data.get("is_featured", False),
                "meta_title": sanitized_data.get("meta_title"),
                "meta_description": sanitized_data.get("meta_description"),
                "meta_keywords": sanitized_data.get("meta_keywords", []),
                "view_count": 0,
                "like_count": 0,
                "dislike_count": 0,
                "comment_count": 0,
                "share_count": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Set publish date if status is published
            if news_data["status"] == "published":
                news_data["published_at"] = datetime.now()
            
            # Create news
            news = self.model.create_news(news_data)
            
            # Log activity
            self.log_activity(author_id, "create", "news", news["_id"], news_data)
            
            # Convert to response DTO
            response_data = NewsResponseDTO(**news)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Berita berhasil dibuat"
            )
            
        except (ValidationException, PermissionException, DuplicateException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal membuat berita",
                code="CREATE_NEWS_ERROR"
            )
    
    def get_news_by_id(self, news_id: str, increment_view: bool = True) -> SuccessResponseDTO:
        """Mendapatkan berita berdasarkan ID"""
        try:
            news = self.model.find_by_id(news_id)
            if not news:
                raise NotFoundException("News", news_id)
            
            # Increment view count if requested
            if increment_view and news["status"] == "published":
                self.model.increment_view_count(news_id)
                news["view_count"] = news.get("view_count", 0) + 1
            
            # Map database fields to DTO fields
            news_data = {
                "id": news.get("id"),
                "title": news.get("title"),
                "slug": news.get("slug"),
                "content": news.get("content"),
                "excerpt": news.get("excerpt", ""),
                "category": news.get("category"),
                "tags": news.get("tags", []),
                "featured_image": news.get("featured_image"),
                "images": news.get("images", []),
                "author_id": news.get("author_id"),
                "author_name": news.get("author_name", ""),
                "author_avatar": news.get("author_avatar"),
                "pesantren_id": news.get("pesantren_id"),
                "pesantren_name": news.get("pesantren_name"),
                "is_published": news.get("status") == "published",
                "is_featured": news.get("is_featured", False),
                "publish_date": news.get("publish_date"),
                "views": news.get("view_count", 0),  # Map view_count to views
                "likes": news.get("likes", 0),
                "dislikes": news.get("dislikes", 0),
                "reading_time": news.get("reading_time", 0),
                "meta_title": news.get("meta_title"),
                "meta_description": news.get("meta_description"),
                "created_at": news.get("created_at"),
                "updated_at": news.get("updated_at")
            }
            
            response_data = NewsResponseDTO(**news_data)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Berita berhasil diambil"
            )
            
        except NotFoundException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil berita",
                code="GET_NEWS_ERROR"
            )
    
    def get_news_by_slug(self, slug: str, increment_view: bool = True) -> SuccessResponseDTO:
        """Mendapatkan berita berdasarkan slug"""
        try:
            news = self.model.find_one({"slug": slug, "status": "published"})
            if not news:
                raise NotFoundException("News", slug)
            
            # Get full details
            news = self.model.get_news_with_details(news["_id"])
            
            # Increment view count if requested
            if increment_view:
                self.model.increment_view_count(news["_id"])
                news["view_count"] = news.get("view_count", 0) + 1
            
            response_data = NewsResponseDTO(**news)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Berita berhasil diambil"
            )
            
        except NotFoundException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil berita",
                code="GET_NEWS_BY_SLUG_ERROR"
            )
    
    def get_news_list(
        self,
        search_params: Optional[Dict[str, Any]] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None,
        include_drafts: bool = False,
        current_user_id: str = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan daftar berita"""
        try:
            # Check permission for drafts
            if include_drafts and current_user_id:
                user = self.user_model.find_by_id(current_user_id)
                if not user or user.get("role") not in ["admin", "editor", "pesantren_admin"]:
                    include_drafts = False
            
            # Validate DTOs
            search_dto = None
            if search_params:
                search_dto = self.validate_dto(NewsSearchDTO, search_params)
            
            filter_dto = None
            if filter_params:
                filter_dto = self.validate_dto(NewsFilterDTO, filter_params)
            
            pagination_dto = PaginationDTO(**(pagination or {}))
            
            # Build query
            query = {}
            
            # Filter by status
            if include_drafts:
                if filter_dto and filter_dto.status:
                    query["status"] = filter_dto.status
            else:
                query["status"] = "published"
            
            # Apply search
            if search_dto and search_dto.query:
                query["$or"] = [
                    {"title": {"$regex": search_dto.query, "$options": "i"}},
                    {"content": {"$regex": search_dto.query, "$options": "i"}},
                    {"excerpt": {"$regex": search_dto.query, "$options": "i"}},
                    {"tags": {"$in": [search_dto.query]}}
                ]
            
            # Apply filters
            if filter_dto:
                if filter_dto.category:
                    query["category"] = filter_dto.category
                if filter_dto.tags:
                    query["tags"] = {"$in": filter_dto.tags}
                if filter_dto.author_id:
                    query["author_id"] = filter_dto.author_id
                if filter_dto.is_featured is not None:
                    query["is_featured"] = filter_dto.is_featured
                if filter_dto.publish_date_from:
                    query["published_at"] = {"$gte": filter_dto.publish_date_from}
                if filter_dto.publish_date_to:
                    query.setdefault("published_at", {})["$lte"] = filter_dto.publish_date_to
            
            # Get data with pagination
            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            # Determine sort order
            sort_order = []
            if search_dto and search_dto.sort_by:
                if search_dto.sort_by == "date":
                    sort_order.append(("published_at", -1 if search_dto.sort_order == "desc" else 1))
                elif search_dto.sort_by == "views":
                    sort_order.append(("view_count", -1 if search_dto.sort_order == "desc" else 1))
                elif search_dto.sort_by == "likes":
                    sort_order.append(("like_count", -1 if search_dto.sort_order == "desc" else 1))
                elif search_dto.sort_by == "title":
                    sort_order.append(("title", 1 if search_dto.sort_order == "asc" else -1))
            else:
                sort_order.append(("published_at", -1))  # Default: newest first
            
            news_list = self.model.search_news(
                query=query,
                skip=skip,
                limit=pagination_dto.limit,
                sort=sort_order
            )
            
            total = self.model.count_documents(query)
            
            # Convert to response DTOs
            response_data = [NewsSummaryDTO(**news).model_dump() for news in news_list]
            
            return self.create_paginated_response(
                data=response_data,
                pagination=pagination_dto,
                total=total,
                message="Daftar berita berhasil diambil"
            )
            
        except ValidationException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil daftar berita",
                code="GET_NEWS_LIST_ERROR"
            )
    
    def get_featured_news(
        self,
        limit: int = 5
    ) -> SuccessResponseDTO:
        """Mendapatkan berita unggulan"""
        try:
            featured_news = self.model.get_published_news(featured=True, limit=limit)
            
            # Convert to response DTOs
            response_data = [NewsSummaryDTO(**news).model_dump() for news in featured_news]
            
            return self.create_success_response(
                data=response_data,
                message="Berita unggulan berhasil diambil"
            )
            
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil berita unggulan",
                code="GET_FEATURED_NEWS_ERROR"
            )
    
    def get_popular_news(
        self,
        days: int = 7,
        limit: int = 10
    ) -> SuccessResponseDTO:
        """Mendapatkan berita populer"""
        try:
            popular_news = self.model.get_popular_news(days, limit)
            
            # Convert to response DTOs
            response_data = [NewsSummaryDTO(**news).model_dump() for news in popular_news]
            
            return self.create_success_response(
                data=response_data,
                message="Berita populer berhasil diambil"
            )
            
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil berita populer",
                code="GET_POPULAR_NEWS_ERROR"
            )
    
    def get_related_news(
        self,
        news_id: str,
        limit: int = 5
    ) -> SuccessResponseDTO:
        """Mendapatkan berita terkait"""
        try:
            # Check if news exists
            news = self.model.find_by_id(news_id)
            if not news:
                raise NotFoundException("News", news_id)
            
            related_news = self.model.get_related_news(news_id, limit)
            
            # Convert to response DTOs
            response_data = [NewsRelatedDTO(**news).dict() for news in related_news]
            
            return self.create_success_response(
                data=response_data,
                message="Berita terkait berhasil diambil"
            )
            
        except NotFoundException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil berita terkait",
                code="GET_RELATED_NEWS_ERROR"
            )
    
    def update_news(
        self, 
        news_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Update berita"""
        try:
            # Check if news exists
            news = self.model.find_by_id(news_id)
            if not news:
                raise NotFoundException("News", news_id)
            
            # Check permission (only author, admin, or editor can update)
            user = self.user_model.find_by_id(user_id)
            if (news["author_id"] != user_id and 
                user.get("role") not in ["admin", "editor"]):
                raise PermissionException("update", "news")
            
            # Validasi input
            update_dto = self.validate_dto(NewsUpdateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(update_dto.dict(exclude_unset=True))
            
            # Check duplicate slug if slug is being updated
            if "slug" in sanitized_data:
                existing_slug = self.model.find_one({
                    "slug": sanitized_data["slug"],
                    "_id": {"$ne": news_id}
                })
                if existing_slug:
                    raise DuplicateException("News", "slug", sanitized_data["slug"])
            
            # Generate excerpt if content is updated but excerpt is not provided
            if "content" in sanitized_data and "excerpt" not in sanitized_data:
                sanitized_data["excerpt"] = self._generate_excerpt(sanitized_data["content"])
            
            # Add update metadata
            sanitized_data["updated_at"] = datetime.now()
            
            # Set publish date if status is changed to published
            if ("status" in sanitized_data and 
                sanitized_data["status"] == "published" and 
                news["status"] != "published"):
                sanitized_data["published_at"] = datetime.now()
            
            # Update news
            updated_news = self.model.update_news(news_id, sanitized_data)
            
            # Log activity
            self.log_activity(user_id, "update", "news", news_id, sanitized_data)
            
            response_data = NewsResponseDTO(**updated_news)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Berita berhasil diperbarui"
            )
            
        except (ValidationException, NotFoundException, PermissionException, DuplicateException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memperbarui berita",
                code="UPDATE_NEWS_ERROR"
            )
    
    def publish_news(
        self, 
        news_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Publikasikan berita"""
        try:
            # Check if news exists
            news = self.model.find_by_id(news_id)
            if not news:
                raise NotFoundException("News", news_id)
            
            # Check permission
            user = self.user_model.find_by_id(user_id)
            if (news["author_id"] != user_id and 
                user.get("role") not in ["admin", "editor"]):
                raise PermissionException("publish", "news")
            
            # Validasi input
            publish_dto = self.validate_dto(NewsPublishDTO, data)
            
            # Prepare publish data
            publish_data = {
                "status": "published",
                "published_at": publish_dto.publish_date or datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Update news
            updated_news = self.model.update_news(news_id, publish_data)
            
            # Log activity
            self.log_activity(user_id, "publish", "news", news_id, publish_data)
            
            response_data = NewsResponseDTO(**updated_news)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Berita berhasil dipublikasikan"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mempublikasikan berita",
                code="PUBLISH_NEWS_ERROR"
            )
    
    def delete_news(self, news_id: str, user_id: str) -> SuccessResponseDTO:
        """Hapus berita (soft delete)"""
        try:
            # Check if news exists
            news = self.model.find_by_id(news_id)
            if not news:
                raise NotFoundException("News", news_id)
            
            # Check permission (only author, admin, or editor can delete)
            user = self.user_model.find_by_id(user_id)
            if (news["author_id"] != user_id and 
                user.get("role") not in ["admin", "editor"]):
                raise PermissionException("delete", "news")
            
            # Soft delete news
            success = self.model.soft_delete_news(news_id)
            if not success:
                return self.create_error_response(
                    message="Gagal menghapus berita",
                    code="DELETE_NEWS_ERROR"
                )
            
            # Log activity
            self.log_activity(user_id, "delete", "news", news_id)
            
            return self.create_success_response(
                data={"id": news_id},
                message="Berita berhasil dihapus"
            )
            
        except (NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal menghapus berita",
                code="DELETE_NEWS_ERROR"
            )
    
    def like_news(
        self, 
        news_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Like/dislike berita"""
        try:
            # Check if news exists
            news = self.model.find_by_id(news_id)
            if not news:
                raise NotFoundException("News", news_id)
            
            # Validasi input
            like_dto = self.validate_dto(NewsLikeDTO, data)
            
            # Check if user already liked/disliked this news
            existing_like = self.model.find_like(news_id, user_id)
            
            if existing_like:
                # Update existing like
                success = self.model.update_like(
                    news_id, 
                    user_id, 
                    like_dto.is_like
                )
            else:
                # Create new like
                success = self.model.like_news(
                    news_id, 
                    user_id, 
                    like_dto.is_like
                )
            
            if not success:
                return self.create_error_response(
                    message="Gagal memberikan like/dislike",
                    code="LIKE_NEWS_ERROR"
                )
            
            # Get updated news
            updated_news = self.model.find_by_id(news_id)
            
            # Log activity
            self.log_activity(user_id, "like" if like_dto.is_like else "dislike", "news", news_id)
            
            return self.create_success_response(
                data={
                    "id": news_id,
                    "like_count": updated_news["like_count"],
                    "dislike_count": updated_news["dislike_count"]
                },
                message="Like/dislike berhasil"
            )
            
        except (ValidationException, NotFoundException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memberikan like/dislike",
                code="LIKE_NEWS_ERROR"
            )
    
    def get_news_stats(
        self, 
        author_id: Optional[str] = None,
        current_user_id: str = None
    ) -> SuccessResponseDTO:
        """Mendapatkan statistik berita"""
        try:
            # Check permission for global stats
            if not author_id and current_user_id:
                user = self.user_model.find_by_id(current_user_id)
                if not user or user.get("role") not in ["admin", "editor"]:
                    raise PermissionException("view", "global news statistics")
            
            raw_stats = self.model.get_news_statistics(author_id)
            
            # Map raw stats to NewsStatsDTO format
            stats = {
                'total_news': raw_stats.get('total_news', 0),
                'published_news': raw_stats.get('published', 0),
                'draft_news': raw_stats.get('draft', 0),
                'featured_news': raw_stats.get('featured', 0),
                'total_views': raw_stats.get('total_views', 0),
                'total_likes': raw_stats.get('total_likes', 0),
                'news_today': 0,  # TODO: implement in model
                'news_this_week': 0,  # TODO: implement in model
                'news_this_month': 0,  # TODO: implement in model
                'by_category': {},  # TODO: implement in model
                'by_author': {},  # TODO: implement in model
                'by_pesantren': {},  # TODO: implement in model
                'trending_tags': [],  # TODO: implement in model
                'popular_news': []  # TODO: implement in model
            }
            
            response_data = NewsStatsDTO(**stats)
            
            return self.create_success_response(
                data=response_data.model_dump(),
                message="Statistik berita berhasil diambil"
            )
            
        except PermissionException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil statistik berita",
                code="NEWS_STATS_ERROR"
            )
    
    def _generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title"""
        import re
        
        # Convert to lowercase and replace spaces with hyphens
        slug = title.lower().replace(" ", "-")
        
        # Remove special characters
        slug = re.sub(r'[^a-z0-9-]', '', slug)
        
        # Remove multiple consecutive hyphens
        slug = re.sub(r'-+', '-', slug)
        
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        
        # Check if slug already exists and add number if needed
        base_slug = slug
        counter = 1
        while self.model.find_one({"slug": slug}):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def _generate_excerpt(self, content: str, max_length: int = 200) -> str:
        """Generate excerpt from content"""
        import re
        
        # Remove HTML tags
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        # Truncate to max length
        if len(clean_content) <= max_length:
            return clean_content
        
        # Find last complete word within limit
        truncated = clean_content[:max_length]
        last_space = truncated.rfind(' ')
        
        if last_space > 0:
            truncated = truncated[:last_space]
        
        return truncated + "..."