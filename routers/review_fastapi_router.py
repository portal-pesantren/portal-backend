from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Create FastAPI router
review_router = APIRouter()

# Pydantic models for request/response
class ReviewCreateRequest(BaseModel):
    pesantren_id: str
    rating: int  # 1-5
    title: str
    content: str
    pros: Optional[List[str]] = []
    cons: Optional[List[str]] = []
    is_anonymous: bool = False

class ReviewUpdateRequest(BaseModel):
    rating: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    is_anonymous: Optional[bool] = None

class ReviewHelpfulRequest(BaseModel):
    is_helpful: bool

class ReviewReportRequest(BaseModel):
    reason: str
    description: Optional[str] = None

class ReviewModerationRequest(BaseModel):
    status: str  # approved, rejected, pending
    reason: Optional[str] = None

# Review endpoints
@review_router.get("/reviews")
async def get_reviews_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    status: Optional[str] = Query(None, description="Filter by status"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """Get list of reviews with pagination and filters"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit,
                "search": search,
                "pesantren_id": pesantren_id,
                "user_id": user_id,
                "rating": rating,
                "status": status,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
        return await router_instance.get_reviews_list(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.get("/reviews/pesantren/{pesantren_id}")
async def get_reviews_by_pesantren(
    pesantren_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    sort_by: Optional[str] = Query("created_at", description="Sort field")
):
    """Get reviews by pesantren"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit,
                "rating": rating,
                "sort_by": sort_by
            }
        }
        
        return await router_instance.get_reviews_by_pesantren(pesantren_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.get("/reviews/user/{user_id}")
async def get_reviews_by_user(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get reviews by user"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit
            }
        }
        
        return await router_instance.get_reviews_by_user(user_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.get("/reviews/stats")
async def get_review_stats(
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren")
):
    """Get review statistics"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        context = {
            "query_params": {
                "pesantren_id": pesantren_id
            }
        }
        
        return await router_instance.get_review_stats(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.get("/reviews/{review_id}")
async def get_review_by_id(review_id: str):
    """Get review by ID"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        return await router_instance.get_review_by_id(review_id, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.post("/reviews")
async def create_review(request: ReviewCreateRequest):
    """Create new review"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.create_review(context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.put("/reviews/{review_id}")
async def update_review(review_id: str, request: ReviewUpdateRequest):
    """Update review"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        context = {
            "data": request.dict(exclude_unset=True)
        }
        
        return await router_instance.update_review(review_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.post("/reviews/{review_id}/helpful")
async def mark_review_helpful(review_id: str, request: ReviewHelpfulRequest):
    """Mark review as helpful/not helpful"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.mark_review_helpful(review_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.post("/reviews/{review_id}/report")
async def report_review(review_id: str, request: ReviewReportRequest):
    """Report review"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.report_review(review_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.patch("/reviews/{review_id}/moderate")
async def moderate_review(review_id: str, request: ReviewModerationRequest):
    """Moderate review (admin only)"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        context = {
            "data": request.dict()
        }
        
        return await router_instance.moderate_review(review_id, context)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.delete("/reviews/{review_id}")
async def delete_review(review_id: str):
    """Delete review (soft delete)"""
    try:
        from routers.review_router import ReviewRouter
        router_instance = ReviewRouter()
        
        return await router_instance.delete_review(review_id, {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))