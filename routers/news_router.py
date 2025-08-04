from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from services.news_service import NewsService
from dto.news_dto import (
    NewsCreateDTO, NewsUpdateDTO, NewsSearchDTO, 
    NewsFilterDTO, NewsStatsDTO
)
# Dependency untuk authentication (placeholder - sesuaikan dengan sistem auth yang ada)
async def get_current_user(token: str = None):
    # TODO: Implement actual authentication logic
    # For now, return a mock user
    return {"user_id": "mock_user_id", "role": "user"}

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user
# from models.user import User  # Not needed with dict-based auth

# Initialize router and service
news_router = APIRouter(prefix="/news", tags=["news"])
news_service = NewsService()

# GET /news - Get all news with pagination, search, and filters
@news_router.get("/")
def get_news_list(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    query: Optional[str] = Query(None),
    sort_by: str = Query("published_at"),
    sort_order: str = Query("desc"),
    pesantren_id: Optional[str] = Query(None),
    author_id: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    is_featured: Optional[bool] = Query(None),
    is_published: Optional[bool] = Query(None),
    published_from: Optional[str] = Query(None),
    published_to: Optional[str] = Query(None)
):
    """Get all news with pagination, search, and filters"""
    try:
        # Create DTOs
        search_dto = NewsSearchDTO(
            query=query or "",
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        filter_dto = NewsFilterDTO(
            pesantren_id=pesantren_id,
            author_id=author_id,
            category=category,
            is_featured=is_featured,
            is_published=is_published,
            published_from=published_from,
            published_to=published_to
        )
        
        # Get news list
        pagination_params = {
            "page": page,
            "limit": limit
        }
        
        search_params = search_dto.dict() if search_dto else None
        filter_params = filter_dto.dict() if filter_dto else None
        
        result = news_service.get_news_list(
            search_params=search_params,
            filter_params=filter_params,
            pagination=pagination_params
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Daftar berita berhasil diambil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /news/featured - Get featured news
@news_router.get("/featured")
def get_featured_news(limit: int = Query(10, ge=1, le=50)):
    """Get featured news"""
    try:
        result = news_service.get_featured_news(limit=limit)
        
        return {
            "success": True,
            "data": result,
            "message": "Berita unggulan berhasil diambil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /news/popular - Get popular news
@news_router.get("/popular")
def get_popular_news(limit: int = Query(10, ge=1, le=50)):
    """Get popular news"""
    try:
        result = news_service.get_popular_news(limit=limit)
        
        return {
            "success": True,
            "data": result,
            "message": "Berita populer berhasil diambil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /news/stats - Get news statistics
@news_router.get("/stats")
def get_news_stats(current_user: dict = Depends(get_current_user)):
    """Get news statistics"""
    try:
        result = news_service.get_news_stats()
        
        return {
            "success": True,
            "data": result,
            "message": "Statistik berita berhasil diambil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET /news/{news_id} - Get news by ID
@news_router.get("/{news_id}")
def get_news_by_id(news_id: str):
    """Get news by ID"""
    try:
        result = news_service.get_news_by_id(news_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Berita tidak ditemukan")
        
        return {
            "success": True,
            "data": result,
            "message": "Detail berita berhasil diambil"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# POST /news - Create new news
@news_router.post("/")
def create_news(
    news_data: NewsCreateDTO,
    current_user: dict = Depends(get_current_admin_user)
):
    """Create new news"""
    try:
        result = news_service.create_news(news_data, current_user.id)
        
        return {
            "success": True,
            "data": result,
            "message": "Berita berhasil dibuat"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT /news/{news_id} - Update news
@news_router.put("/{news_id}")
def update_news(
    news_id: str,
    news_data: NewsUpdateDTO,
    current_user: dict = Depends(get_current_admin_user)
):
    """Update news"""
    try:
        result = news_service.update_news(news_id, news_data, current_user.get("user_id"))
        
        return {
            "success": True,
            "data": result,
            "message": "Berita berhasil diperbarui"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE /news/{news_id} - Delete news
@news_router.delete("/{news_id}")
def delete_news(
    news_id: str,
    current_user: dict = Depends(get_current_admin_user)
):
    """Delete news"""
    try:
        result = news_service.delete_news(news_id, current_user.id)
        
        return {
            "success": True,
            "data": result,
            "message": "Berita berhasil dihapus"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))