from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

# Create FastAPI router
application_router = APIRouter()

# Pydantic models for request/response
class ApplicationCreateRequest(BaseModel):
    pesantren_id: str
    program_id: str
    full_name: str
    birth_date: str
    birth_place: str
    gender: str
    address: str
    phone: str
    email: str
    parent_name: str
    parent_phone: str
    education_level: str
    previous_school: Optional[str] = None
    motivation: str
    health_condition: Optional[str] = None
    special_needs: Optional[str] = None

class ApplicationUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    gender: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    parent_name: Optional[str] = None
    parent_phone: Optional[str] = None
    education_level: Optional[str] = None
    previous_school: Optional[str] = None
    motivation: Optional[str] = None
    health_condition: Optional[str] = None
    special_needs: Optional[str] = None

class ApplicationStatusRequest(BaseModel):
    status: str  # pending, approved, rejected, interview_scheduled, enrolled
    notes: Optional[str] = None

class InterviewScheduleRequest(BaseModel):
    interview_date: str
    interview_time: str
    interview_location: str
    interviewer: str
    notes: Optional[str] = None

# Application endpoints
@application_router.get("/applications")
async def get_applications_list(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    search: Optional[str] = Query(None, description="Search term"),
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren"),
    user_id: Optional[str] = Query(None, description="Filter by user"),
    status: Optional[str] = Query(None, description="Filter by status"),
    program_id: Optional[str] = Query(None, description="Filter by program"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order")
):
    """Get list of applications with pagination and filters"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit,
                "search": search,
                "pesantren_id": pesantren_id,
                "user_id": user_id,
                "status": status,
                "program_id": program_id,
                "sort_by": sort_by,
                "sort_order": sort_order
            }
        }
        
        # Use handle_request method instead of calling get_applications_list directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-applications-list",
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

@application_router.get("/applications/pesantren/{pesantren_id}")
async def get_applications_by_pesantren(
    pesantren_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[str] = Query(None, description="Filter by status"),
    program_id: Optional[str] = Query(None, description="Filter by program")
):
    """Get applications by pesantren"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit,
                "status": status,
                "program_id": program_id
            }
        }
        
        # Use handle_request method instead of calling get_applications_by_pesantren directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-applications-by-pesantren",
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

@application_router.get("/applications/user/{user_id}")
async def get_applications_by_user(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page")
):
    """Get applications by user"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        context = {
            "query_params": {
                "page": page,
                "limit": limit
            }
        }
        
        # Use handle_request method instead of calling get_applications_by_user directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-applications-by-user",
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

@application_router.get("/applications/stats")
async def get_application_stats(
    pesantren_id: Optional[str] = Query(None, description="Filter by pesantren")
):
    """Get application statistics"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        context = {
            "query_params": {
                "pesantren_id": pesantren_id
            }
        }
        
        # Use handle_request method instead of calling get_application_stats directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-application-stats",
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

@application_router.get("/applications/{application_id}")
async def get_application_by_id(application_id: str):
    """Get application by ID"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        # Use handle_request method instead of calling get_application_by_id directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-application-by-id",
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

@application_router.post("/applications")
async def create_application(request: ApplicationCreateRequest):
    """Create new application"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling create_application directly
        response = router_instance.handle_request(
            method="POST",
            path="/create-application",
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

@application_router.put("/applications/{application_id}")
async def update_application(application_id: str, request: ApplicationUpdateRequest):
    """Update application"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        context = {
            "data": request.dict(exclude_unset=True)
        }
        
        # Use handle_request method instead of calling update_application directly
        response = router_instance.handle_request(
            method="PUT",
            path="/update-application",
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

@application_router.patch("/applications/{application_id}/status")
async def update_application_status(application_id: str, request: ApplicationStatusRequest):
    """Update application status"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling update_application_status directly
        response = router_instance.handle_request(
            method="PUT",
            path="/update-application-status",
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

@application_router.post("/applications/{application_id}/schedule-interview")
async def schedule_interview(application_id: str, request: InterviewScheduleRequest):
    """Schedule interview for application"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        context = {
            "data": request.dict()
        }
        
        # Use handle_request method instead of calling schedule_interview directly
        response = router_instance.handle_request(
            method="PATCH",
            path="/schedule-interview",
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

@application_router.post("/applications/{application_id}/upload-document")
async def upload_document(
    application_id: str,
    document_type: str = Query(..., description="Type of document"),
    file: UploadFile = File(...)
):
    """Upload document for application"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        context = {
            "data": {
                "document_type": document_type,
                "file": file
            }
        }
        
        # Use handle_request method instead of calling upload_document directly
        response = router_instance.handle_request(
            method="GET",
            path="/upload-document",
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

@application_router.get("/applications/{application_id}/documents")
async def get_application_documents(application_id: str):
    """Get application documents"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        # Use handle_request method instead of calling get_application_documents directly
        response = router_instance.handle_request(
            method="GET",
            path="/get-application-documents",
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

@application_router.delete("/applications/{application_id}")
async def cancel_application(application_id: str):
    """Cancel application"""
    try:
        from routers.application_router import ApplicationRouter
        router_instance = ApplicationRouter()
        
        # Use handle_request method instead of calling cancel_application directly
        response = router_instance.handle_request(
            method="GET",
            path="/cancel-application",
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