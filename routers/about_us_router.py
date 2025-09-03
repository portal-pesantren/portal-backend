from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict
from services.about_us import AboutUsService
from dto.about_us_dto import AboutUsUpdateDTO
from dto.base_dto import SuccessResponseDTO
from core.auth_middleware import require_role
from core.exceptions import ServiceException

about_us_router = APIRouter()
about_us_service = AboutUsService()

@about_us_router.get("/about-us", response_model=SuccessResponseDTO, tags=["About Us"])
async def get_about_us_content():
    """
    Mengambil konten halaman 'About Us'.
    Endpoint ini dapat diakses secara publik.
    """
    try:
        return about_us_service.get_about_us()
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)

@about_us_router.put("/about-us", response_model=SuccessResponseDTO, tags=["About Us"])
async def update_about_us_content(
    update_data: AboutUsUpdateDTO,
    current_user: Dict = Depends(require_role("admin"))
):
    """
    Membuat atau memperbarui konten halaman 'About Us'.
    Endpoint ini memerlukan hak akses admin.
    """
    try:
        user_id = current_user.get("id")
        return about_us_service.update_about_us(data=update_data.dict(), user_id=user_id)
    except ServiceException as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))