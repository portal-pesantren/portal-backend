from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Create FastAPI router
consultation_router = APIRouter()

# Pydantic models for request/response
class ConsultationCreateRequest(BaseModel):
    title: str
    description: str
    category: str
    priority: Optional[str] = "medium"  # low, medium, high, urgent
    pesantren_id: Optional[str] = None
    is_anonymous: bool = False
    contact_method: Optional[str] = "platform"  # platform, email, phone, whatsapp
    preferred_time: Optional[str] = None

class ConsultationUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    pesantren_id: Optional[str] = None
    is_anonymous: Optional[bool] = None
    contact_method: Optional[str] = None
    preferred_time: Optional[str] = None

class ConsultationResponseRequest(BaseModel):
    content: str
    is_solution: bool = False
    attachments: Optional[List[str]] = []

class ConsultationAssignRequest(BaseModel):
    consultant_id: str
    notes: Optional[str] = None

class ConsultationStatusRequest(BaseModel):
    status: str  # open, in_progress, resolved, closed
    notes: Optional[str] = None

class ConsultationRatingRequest(BaseModel):
    rating: int  # 1-5
    feedback: Optional[str] = None

# Consultation endpoints
@consultation_router.get("/consultations")
async def get_consultations_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    consultant_id: Optional[str] = Query(None, description="Filter by consultant"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """Get list of consultations with pagination and filters"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit,
                "search": search,
                "category": category,
                "status": status,
                "priority": priority,
                "pesantren_id": pesantren_id,
                "user_id": user_id,
                "consultant_id": consultant_id,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
        # Use handle_request method instead of calling get_consultations_list directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-consultations-list",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.get("/consultations/stats")
async def get_consultation_stats(
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren"),
    consultant_id: Optional[str] = Query(None, description="Filter by consultant"),
    period: Optional[str] = Query("month", description="Time period (day, week, month, year)")
):
    """Get consultation statistics"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "query_params": {
                "pesantren_id": pesantren_id,
                "consultant_id": consultant_id,
                "period": period
            }
        }
        
        # Use handle_request method instead of calling get_consultation_stats directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-consultation-stats",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.get("/consultations/analytics")
async def get_consultation_analytics(
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """Get consultation analytics"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "query_params": {
                "pesantren_id": pesantren_id,
                "start_date": start_date,
                "end_date": end_date
            }
        }
        
        # Use handle_request method instead of calling get_consultation_analytics directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-consultation-analytics",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.get("/consultations/categories")
async def get_consultation_categories():
    """Get consultation categories"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        # Use handle_request method instead of calling get_consultation_categories directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-consultation-categories",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.get("/consultations/{consultation_id}")
async def get_consultation_by_id(consultation_id: str):
    """Get consultation by ID"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        # Use handle_request method instead of calling get_consultation_by_id directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-consultation-by-id",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.post("/consultations")
async def create_consultation(request: ConsultationCreateRequest):
    """Create new consultation"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling create_consultation directly
        response = router_instance.handle_request(
            method="POST",
            path="/create-consultation",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.put("/consultations/{consultation_id}")
async def update_consultation(consultation_id: str, request: ConsultationUpdateRequest):
    """Update consultation"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "data": request.dict(exclude_unset=True)
        }
        
        # Use handle_request method instead of calling update_consultation directly
        response = router_instance.handle_request(
            method="PUT",
            path="/update-consultation",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.post("/consultations/{consultation_id}/responses")
async def create_consultation_response(consultation_id: str, request: ConsultationResponseRequest):
    """Create consultation response"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling create_consultation_response directly
        response = router_instance.handle_request(
            method="POST",
            path="/create-consultation-response",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.get("/consultations/{consultation_id}/responses")
async def get_consultation_responses(
    consultation_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page")
):
    """Get consultation responses"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit
            }
        }
        
        # Use handle_request method instead of calling get_consultation_responses directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-consultation-responses",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.patch("/consultations/{consultation_id}/assign")
async def assign_consultant(consultation_id: str, request: ConsultationAssignRequest):
    """Assign consultant to consultation"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling assign_consultant directly
        response = router_instance.handle_request(
            method="PATCH",
            path="/assign-consultant",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.patch("/consultations/{consultation_id}/status")
async def update_consultation_status(consultation_id: str, request: ConsultationStatusRequest):
    """Update consultation status"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling update_consultation_status directly
        response = router_instance.handle_request(
            method="PUT",
            path="/update-consultation-status",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.post("/consultations/{consultation_id}/rating")
async def rate_consultation(consultation_id: str, request: ConsultationRatingRequest):
    """Rate consultation"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling rate_consultation directly
        response = router_instance.handle_request(
            method="PATCH",
            path="/rate-consultation",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@consultation_router.delete("/consultations/{consultation_id}")
async def delete_consultation(consultation_id: str):
    """Delete consultation (soft delete)"""
    try:
        from routers.consultation_router import ConsultationRouter
        router_instance = ConsultationRouter()
        
        # Use handle_request method instead of calling delete_consultation directly
        response = router_instance.handle_request(
            method="DELETE",
            path="/delete-consultation",
            data={},
            headers={"Content-Type": "application/json"}
        )
        
        # Check if response indicates an error
        if response.get("status_code", 200) >= 400:
            raise HTTPException(
                status_code=response.get("status_code", 500),
                detail=response.get("message", "Internal server error")
            )
        
        return response
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))