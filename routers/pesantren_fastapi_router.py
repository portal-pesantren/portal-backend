from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List
from pydantic import BaseModel

# Create FastAPI router
pesantren_router = APIRouter()

# Pydantic models for request/response
class PesantrenCreateRequest(BaseModel):
    name: str
    description: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    capacity: Optional[int] = None
    facilities: Optional[List[str]] = []
    programs: Optional[List[str]] = []
    is_active: bool = True

class PesantrenUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    capacity: Optional[int] = None
    facilities: Optional[List[str]] = None
    programs: Optional[List[str]] = None
    is_active: Optional[bool] = None

class FeaturedRequest(BaseModel):
    is_featured: bool

# Pesantren endpoints
@pesantren_router.get("/pesantren")
async def get_pesantren_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    location: Optional[str] = Query(None, description="Filter by location"),
    program: Optional[str] = Query(None, description="Filter by program"),
    is_active: Optional[bool] = Query(None, description="Filter by active status")
):
    """Get list of pesantren with pagination and filters"""
    try:
        # Import router class and create instance
        from routers.pesantren_router import PesantrenRouter
        router_instance = PesantrenRouter()
        
        # Prepare request context
        context = {
            "query_params": {
                "page": page,
                "limit": limit,
                "search": search,
                "location": location,
                "program": program,
                "is_active": is_active
            }
        }
        
        # Use handle_request method instead of calling get_pesantren_list directly
        response = router_instance.handle_request(
            method="GET",
            path="/pesantren",
            data={},
            headers={"Content-Type": "application/json"},
            query_params={
                "page": str(page),
                "limit": str(limit),
                "search": search,
                "location": location,
                "category": category,
                "is_active": str(is_active) if is_active is not None else None
            }
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
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@pesantren_router.get("/pesantren/featured")
async def get_featured_pesantren(
    limit: int = Query(5, ge=1, le=20, description="Number of featured pesantren")
):
    """Get featured pesantren"""
    try:
        from routers.pesantren_router import PesantrenRouter
        router_instance = PesantrenRouter()
        
        context = {
            "query_params": {"limit": limit}
        }
        
        # Use handle_request method instead of calling get_featured_pesantren directly
        response = router_instance.handle_request(
            method="GET",
            path="/pesantren/featured",
            data={},
            headers={"Content-Type": "application/json"},
            query_params={"limit": str(limit)}
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
    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@pesantren_router.get("/pesantren/popular")
async def get_popular_pesantren(
    limit: int = Query(5, ge=1, le=20, description="Number of popular pesantren")
):
    """Get popular pesantren"""
    try:
        from routers.pesantren_router import PesantrenRouter
        router_instance = PesantrenRouter()
        
        context = {
            "query_params": {"limit": limit}
        }
        
        # Use handle_request method instead of calling get_popular_pesantren directly
        response = router_instance.handle_request(
            method="GET",
            path="/pesantren/popular",
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

@pesantren_router.get("/pesantren/stats")
async def get_pesantren_stats():
    """Get pesantren statistics"""
    try:
        from routers.pesantren_router import PesantrenRouter
        router_instance = PesantrenRouter()
        
        # Use handle_request method instead of calling get_pesantren_stats directly
        response = router_instance.handle_request(
            method="GET",
            path="/pesantren/stats",
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

@pesantren_router.get("/pesantren/{pesantren_id}")
async def get_pesantren_by_id(pesantren_id: str):
    """Get pesantren by ID"""
    try:
        from routers.pesantren_router import PesantrenRouter
        router_instance = PesantrenRouter()
        
        # Use handle_request method instead of calling get_pesantren_by_id directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-pesantren-by-id",
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

@pesantren_router.post("/pesantren")
async def create_pesantren(request: PesantrenCreateRequest):
    """Create new pesantren"""
    try:
        from routers.pesantren_router import PesantrenRouter
        router_instance = PesantrenRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling create_pesantren directly
        response = router_instance.handle_request(
            method="POST",
            path="/create-pesantren",
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

@pesantren_router.put("/pesantren/{pesantren_id}")
async def update_pesantren(pesantren_id: str, request: PesantrenUpdateRequest):
    """Update pesantren"""
    try:
        from routers.pesantren_router import PesantrenRouter
        router_instance = PesantrenRouter()
        
        context = {
            "data": request.dict(exclude_unset=True)
        }
        
        # Use handle_request method instead of calling update_pesantren directly
        response = router_instance.handle_request(
            method="PUT",
            path="/update-pesantren",
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

@pesantren_router.patch("/pesantren/{pesantren_id}/featured")
async def set_pesantren_featured(pesantren_id: str, request: FeaturedRequest):
    """Set pesantren featured status"""
    try:
        from routers.pesantren_router import PesantrenRouter
        router_instance = PesantrenRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling set_pesantren_featured directly
        response = router_instance.handle_request(
            method="PATCH",
            path="/set-pesantren-featured",
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

@pesantren_router.delete("/pesantren/{pesantren_id}")
async def delete_pesantren(pesantren_id: str):
    """Delete pesantren (soft delete)"""
    try:
        from routers.pesantren_router import PesantrenRouter
        router_instance = PesantrenRouter()
        
        # Use handle_request method instead of calling delete_pesantren directly
        response = router_instance.handle_request(
            method="DELETE",
            path="/delete-pesantren",
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