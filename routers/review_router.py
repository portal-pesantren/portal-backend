from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from services.review_service import ReviewService
from dto.review_dto import (
    ReviewCreateDTO, ReviewUpdateDTO, ReviewSearchDTO, 
    ReviewFilterDTO, ReviewStatsDTO, ReviewModerationDTO
)

# Create FastAPI router
review_router = APIRouter()

# Initialize service
review_service = ReviewService()

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

# Dependency untuk authentication (placeholder - sesuaikan dengan sistem auth yang ada)
async def get_current_user(token: str = None):
    # TODO: Implement actual authentication logic
    # For now, return a mock user
    return {"user_id": "mock_user_id", "role": "user"}

async def get_current_admin_user(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Review endpoints
@review_router.get("/reviews")
async def get_reviews_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    rating: Optional[int] = Query(None, ge=1, le=5, description="Filter by rating"),
    min_rating: Optional[int] = Query(None, ge=1, le=5, description="Minimum rating"),
    max_rating: Optional[int] = Query(None, ge=1, le=5, description="Maximum rating"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    status: Optional[str] = Query(None, description="Filter by status"),
    created_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    created_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """Get list of reviews with pagination and filters"""
    try:
        # Create DTOs
        search_dto = ReviewSearchDTO(
            query=search or "",
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        filter_dto = ReviewFilterDTO(
            pesantren_id=pesantren_id,
            user_id=user_id,
            rating=rating,
            min_rating=min_rating,
            max_rating=max_rating,
            is_verified=is_verified,
            status=status,
            created_from=created_from,
            created_to=created_to
        )
        
        # Get reviews list
        result = review_service.get_reviews_list(
            page=page,
            limit=limit,
            search=search_dto,
            filters=filter_dto
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Daftar ulasan berhasil diambil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.get("/reviews/pesantren/{pesantren_id}")
async def get_reviews_by_pesantren(
    pesantren_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """Get reviews by pesantren"""
    try:
        # Create search DTO
        search_dto = ReviewSearchDTO(
            query=search or "",
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get reviews by pesantren
        result = review_service.get_reviews_by_pesantren(
            pesantren_id=pesantren_id,
            page=page,
            limit=limit,
            search=search_dto
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Ulasan pesantren berhasil diambil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.get("/reviews/user/{user_id}")
async def get_reviews_by_user(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order"),
    current_user: dict = Depends(get_current_user)
):
    """Get reviews by user"""
    try:
        # Check if user can access these reviews
        if current_user["user_id"] != user_id and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=403,
                detail="Anda tidak memiliki akses untuk melihat ulasan pengguna ini"
            )
        
        # Create search DTO
        search_dto = ReviewSearchDTO(
            query=search or "",
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        # Get reviews by user
        result = review_service.get_reviews_by_user(
            user_id=user_id,
            page=page,
            limit=limit,
            search=search_dto
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Ulasan pengguna berhasil diambil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.get("/reviews/stats")
async def get_review_stats(
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren"),
    group_by: Optional[str] = Query("rating", description="Group by field"),
    include_trends: Optional[bool] = Query(False, description="Include trend data")
):
    """Get review statistics"""
    try:
        stats_dto = ReviewStatsDTO(
            pesantren_id=pesantren_id,
            group_by=group_by,
            include_trends=include_trends
        )
        
        result = review_service.get_review_stats(stats_dto)
        
        return {
            "success": True,
            "data": result,
            "message": "Statistik ulasan berhasil diambil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.get("/reviews/{review_id}")
async def get_review_by_id(review_id: str):
    """Get review by ID"""
    try:
        result = review_service.get_review_by_id(review_id)
        
        return {
            "success": True,
            "data": result,
            "message": "Detail ulasan berhasil diambil"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.post("/reviews")
async def create_review(
    review_data: ReviewCreateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Create new review"""
    try:
        # Add user_id to data
        create_dto = ReviewCreateDTO(
            user_id=current_user["user_id"],
            pesantren_id=review_data.pesantren_id,
            rating=review_data.rating,
            title=review_data.title,
            content=review_data.content,
            pros=review_data.pros,
            cons=review_data.cons,
            is_anonymous=review_data.is_anonymous
        )
        
        # Create review
        result = review_service.create_review(create_dto)
        
        return {
            "success": True,
            "data": result,
            "message": "Ulasan berhasil dibuat"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.put("/reviews/{review_id}")
async def update_review(
    review_id: str,
    review_data: ReviewUpdateRequest,
    current_user: dict = Depends(get_current_user)
):
    """Update review"""
    try:
        # Create DTO
        update_dto = ReviewUpdateDTO(
            rating=review_data.rating,
            title=review_data.title,
            content=review_data.content,
            pros=review_data.pros,
            cons=review_data.cons,
            is_anonymous=review_data.is_anonymous
        )
        
        # Update review
        result = review_service.update_review(review_id, update_dto, current_user["user_id"])
        
        return {
            "success": True,
            "data": result,
            "message": "Ulasan berhasil diperbarui"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.post("/reviews/{review_id}/helpful")
async def mark_helpful(
    review_id: str,
    helpful_data: ReviewHelpfulRequest,
    current_user: dict = Depends(get_current_user)
):
    """Mark review as helpful"""
    try:
        # Mark as helpful
        result = review_service.mark_helpful(review_id, current_user["user_id"])
        
        return {
            "success": True,
            "data": result,
            "message": "Ulasan berhasil ditandai sebagai bermanfaat"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.post("/reviews/{review_id}/report")
async def report_review(
    review_id: str,
    report_data: ReviewReportRequest,
    current_user: dict = Depends(get_current_user)
):
    """Report review"""
    try:
        # Report review
        result = review_service.report_review(
            review_id, 
            current_user["user_id"], 
            report_data.reason
        )
        
        return {
            "success": True,
            "data": result,
            "message": "Ulasan berhasil dilaporkan"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.post("/reviews/{review_id}/moderate")
async def moderate_review(
    review_id: str,
    moderation_data: ReviewModerationRequest,
    current_user: dict = Depends(get_current_admin_user)
):
    """Moderate review (admin only)"""
    try:
        # Create DTO
        moderation_dto = ReviewModerationDTO(
            status=moderation_data.status,
            reason=moderation_data.reason,
            moderator_id=current_user["user_id"]
        )
        
        # Moderate review
        result = review_service.moderate_review(review_id, moderation_dto)
        
        return {
            "success": True,
            "data": result,
            "message": "Ulasan berhasil dimoderasi"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@review_router.delete("/reviews/{review_id}")
async def delete_review(
    review_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete review (soft delete)"""
    try:
        # Delete review
        result = review_service.delete_review(review_id, current_user["user_id"])
        
        return {
            "success": True,
            "data": result,
            "message": "Ulasan berhasil dihapus"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))