from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Create FastAPI router
news_router = APIRouter()

# Pydantic models for request/response
class NewsCreateRequest(BaseModel):
    title: str
    slug: Optional[str] = None
    content: str
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    category: str
    tags: Optional[List[str]] = []
    pesantren_id: Optional[str] = None
    is_featured: bool = False
    is_published: bool = False
    publish_date: Optional[str] = None

class NewsUpdateRequest(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    excerpt: Optional[str] = None
    featured_image: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    pesantren_id: Optional[str] = None
    is_featured: Optional[bool] = None
    is_published: Optional[bool] = None
    publish_date: Optional[str] = None

class NewsPublishRequest(BaseModel):
    is_published: bool
    publish_date: Optional[str] = None

class NewsLikeRequest(BaseModel):
    action: str  # like, dislike, remove

# News endpoints
@news_router.get("/news")
async def get_news_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Filter by category"),
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren"),
    is_featured: Optional[bool] = Query(None, description="Filter by featured"),
    is_published: Optional[bool] = Query(None, description="Filter by published"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma separated)"),
    sort_by: Optional[str] = Query("publish_date", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """Get list of news with pagination and filters"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit,
                "search": search,
                "category": category,
                "pesantren_id": pesantren_id,
                "is_featured": is_featured,
                "is_published": is_published,
                "tags": tags.split(",") if tags else None,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
        return await router_instance.get_news_list(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.get("/news/featured")
async def get_featured_news(
    limit: int = Query(5, ge=1, le=20, description="Number of featured news")
):
    """Get featured news"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "query_params": {"limit": limit}
        }
        
        return await router_instance.get_featured_news(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.get("/news/popular")
async def get_popular_news(
    limit: int = Query(5, ge=1, le=20, description="Number of popular news"),
    period: Optional[str] = Query("week", description="Time period (day, week, month)")
):
    """Get popular news"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "query_params": {
                "limit": limit,
                "period": period
            }
        }
        
        return await router_instance.get_popular_news(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.get("/news/stats")
async def get_news_stats(
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren")
):
    """Get news statistics"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "query_params": {
                "pesantren_id": pesantren_id
            }
        }
        
        return await router_instance.get_news_stats(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.get("/news/categories")
async def get_news_categories():
    """Get news categories"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        return await router_instance.get_news_categories({})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.get("/news/tags")
async def get_news_tags(
    limit: Optional[int] = Query(50, description="Number of tags to return")
):
    """Get news tags"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "query_params": {"limit": limit}
        }
        
        return await router_instance.get_news_tags(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.get("/news/slug/{slug}")
async def get_news_by_slug(slug: str):
    """Get news by slug"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        return await router_instance.get_news_by_slug(slug, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.get("/news/{news_id}")
async def get_news_by_id(news_id: str):
    """Get news by ID"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        return await router_instance.get_news_by_id(news_id, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.get("/news/{news_id}/related")
async def get_related_news(
    news_id: str,
    limit: int = Query(5, ge=1, le=10, description="Number of related news")
):
    """Get related news"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "query_params": {"limit": limit}
        }
        
        return await router_instance.get_related_news(news_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.post("/news")
async def create_news(request: NewsCreateRequest):
    """Create new news"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.create_news(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.put("/news/{news_id}")
async def update_news(news_id: str, request: NewsUpdateRequest):
    """Update news"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "data": request.dict(exclude_unset=True)
        }
        
        return await router_instance.update_news(news_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.patch("/news/{news_id}/publish")
async def publish_news(news_id: str, request: NewsPublishRequest):
    """Publish/unpublish news"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.publish_news(news_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.post("/news/{news_id}/like")
async def like_news(news_id: str, request: NewsLikeRequest):
    """Like/dislike news"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.like_news(news_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.post("/news/{news_id}/view")
async def increment_news_view(news_id: str):
    """Increment news view count"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        return await router_instance.increment_news_view(news_id, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@news_router.delete("/news/{news_id}")
async def delete_news(news_id: str):
    """Delete news (soft delete)"""
    try:
        from routers.news_router import NewsRouter
        router_instance = NewsRouter()
        
        return await router_instance.delete_news(news_id, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))