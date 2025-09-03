import logging

from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi import status as http_status
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from services.pesantren_service import PesantrenService
from core.exceptions import ValidationException, ServiceException, DuplicateException
from dto.pesantren_dto import (
    PesantrenCreateDTO, PesantrenUpdateDTO, PesantrenSearchDTO, 
    PesantrenFilterDTO, PesantrenStatsDTO, PesantrenResponseDTO,
    PesantrenSummaryDTO
)
from dto.base_dto import PaginatedResponseDTO, SuccessResponseDTO
from core.auth_middleware import require_role

# Request models
class FeaturedStatusRequest(BaseModel):
    is_featured: bool

# Create FastAPI router
pesantren_router = APIRouter()

# Initialize service
pesantren_service = PesantrenService()

# GET /pesantren - Get all pesantren with pagination, search, and filters
@pesantren_router.get("/pesantren", response_model=PaginatedResponseDTO)
async def get_pesantren_list(
    page: int = Query(1, ge=1, description="Nomor halaman"),
    limit: int = Query(10, ge=1, le=100, description="Jumlah item per halaman"),
    query: Optional[str] = Query(None, description="Kata kunci pencarian"),
    sort_by: str = Query("created_at", description="Field untuk sorting"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="Urutan sorting"),
    province: Optional[str] = Query(None, description="Filter provinsi"),
    city: Optional[str] = Query(None, description="Filter kota"),
    type: Optional[str] = Query(None, description="Filter tipe pesantren"),
    is_featured: Optional[bool] = Query(None, description="Filter pesantren unggulan"),
    status: Optional[str] = Query(None, description="Filter status"),
    min_capacity: Optional[int] = Query(None, ge=0, description="Kapasitas minimum"),
    max_capacity: Optional[int] = Query(None, ge=0, description="Kapasitas maksimum"),
    has_scholarship: Optional[bool] = Query(None, description="Filter ada beasiswa")
):
    """Mendapatkan daftar pesantren dengan paginasi, pencarian, dan filter"""
    try:
        # Set default values jika query tidak diisi (query opsional)
        if not query:
            # Default: urutkan dari yang terbaru
            sort_by = sort_by or "created_at"
            sort_order = sort_order or "desc"
        
        # Create DTOs
        search_dto = PesantrenSearchDTO(
            query=query or "",
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        filter_dto = PesantrenFilterDTO(
            province=province,
            city=city,
            type=type,
            is_featured=is_featured,
            status=status,
            min_capacity=min_capacity,
            max_capacity=max_capacity,
            has_scholarship=has_scholarship
        )
        
        # Get pesantren list
        result = pesantren_service.get_pesantren_list(
            search_params=search_dto.dict() if search_dto.query else None,
            filter_params=filter_dto.dict(exclude_unset=True),
            pagination={"page": page, "limit": limit}
        )
        
        return result
        
    except ValidationException as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        logging.error(f"Error in get_pesantren_list: {str(e)}")
        logging.error(f"Error type: {type(e).__name__}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal server"
        )
        
# GET /pesantren/featured - Get featured pesantren
@pesantren_router.get("/pesantren/featured", response_model=SuccessResponseDTO)
async def get_featured_pesantren(
    limit: int = Query(10, ge=1, le=50, description="Jumlah pesantren unggulan")
):
    """Mendapatkan daftar pesantren unggulan"""
    try:
        result = pesantren_service.get_featured_pesantren(limit=limit)
        return result
        
    except ServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal server"
        )

# GET /pesantren/popular - Get popular pesantren
@pesantren_router.get("/pesantren/popular", response_model=SuccessResponseDTO)
async def get_popular_pesantren(
    limit: int = Query(10, ge=1, le=50, description="Jumlah pesantren populer")
):
    """Mendapatkan daftar pesantren populer"""
    try:
        result = pesantren_service.get_popular_pesantren(limit=limit)
        return result
        
    except ServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal server"
        )

# GET /pesantren/stats - Get pesantren statistics
@pesantren_router.get("/pesantren/stats")
async def get_pesantren_stats():
    """Mendapatkan statistik pesantren"""
    try:
        result = pesantren_service.get_pesantren_stats()
        return result
        
    except ServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal server"
        )

# GET /pesantren/{pesantren_id} - Get pesantren by ID
@pesantren_router.get("/pesantren/{pesantren_id}", response_model=SuccessResponseDTO)
async def get_pesantren_by_id(pesantren_id: str):
    """Mendapatkan detail pesantren berdasarkan ID"""
    try:
        result = pesantren_service.get_pesantren_by_id(pesantren_id)
        
        if not result:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Pesantren tidak ditemukan"
            )
            
        return result
        
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal server"
        )
        
# POST /pesantren - Create new pesantren
@pesantren_router.post("/pesantren", status_code=http_status.HTTP_201_CREATED, response_model=PesantrenResponseDTO)
async def create_pesantren(
    create_dto: PesantrenCreateDTO,
    # Ganti placeholder dengan dependency injection untuk autentikasi
    current_user: dict = Depends(require_role("admin")) 
):
    try:
        # Ambil ID user yang login dari token
        user_id = current_user.get("id")
        
        result = pesantren_service.create_pesantren(create_dto.dict(), user_id)
        
        # Service sudah mengembalikan SuccessResponseDTO, kita ambil datanya
        return result.data

    except (ValidationException, DuplicateException) as e:
        raise HTTPException(status_code=http_status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ServiceException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        import traceback
        logging.error(f"Error in create_pesantren: {str(e)}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal server"
        )

# PUT /pesantren/{pesantren_id} - Update pesantren
@pesantren_router.put("/pesantren/{pesantren_id}", response_model=SuccessResponseDTO)
async def update_pesantren(pesantren_id: str, update_dto: PesantrenUpdateDTO):
    """Memperbarui data pesantren (Admin only)"""
    try:
        # TODO: Get user_id from authentication context
        user_id = "admin"  # Temporary placeholder
        
        # Update pesantren
        result = pesantren_service.update_pesantren(pesantren_id, update_dto.dict(exclude_unset=True), user_id)
        
        if not result:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Pesantren tidak ditemukan"
            )
            
        return result
        
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal server"
        )

# PATCH /pesantren/{pesantren_id}/featured - Set featured status
@pesantren_router.patch("/pesantren/{pesantren_id}/featured", response_model=SuccessResponseDTO)
async def set_featured_status(pesantren_id: str, featured_request: FeaturedStatusRequest):
    """Mengatur status unggulan pesantren (Admin only)"""
    try:
        # TODO: Get user_id from authentication context
        user_id = "admin"  # Temporary placeholder
        
        is_featured = featured_request.is_featured
        
        # Set featured status
        result = pesantren_service.set_featured_status(pesantren_id, is_featured, user_id)
        
        if not result:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Pesantren tidak ditemukan"
            )
            
        return result
        
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal server"
        )

# DELETE /pesantren/{pesantren_id} - Delete pesantren (soft delete)
@pesantren_router.delete("/pesantren/{pesantren_id}", response_model=SuccessResponseDTO)
async def delete_pesantren(pesantren_id: str):
    """Menghapus pesantren (soft delete) (Admin only)"""
    try:
        # TODO: Get user_id from authentication context
        user_id = "admin"  # Temporary placeholder
        
        # Delete pesantren
        result = pesantren_service.delete_pesantren(pesantren_id, user_id)
        
        if not result:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Pesantren tidak ditemukan"
            )
            
        return result
        
    except HTTPException:
        raise
    except ValidationException as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=e.message
        )
    except ServiceException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message
        )
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Terjadi kesalahan internal server"
        )