# routers/news_router.py

from typing import Any, List
from fastapi import APIRouter, Depends, Query, Body, Path, status, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# Ganti import ini dengan struktur proyek Anda
from services.news_service import NewsService, NotFoundException
from dto.news_dto import (
    NewsCreateDTO, NewsUpdateDTO, NewsSearchDTO, NewsFilterDTO, 
    NewsResponseDTO, NewsSummaryDTO, NewsFeatureDTO
)
from dto.base_dto import (
    SuccessResponseDTO, PaginatedResponseDTO, ErrorResponseDTO, 
    ValidationErrorResponseDTO, ValidationErrorDTO
)

news_service = NewsService()
news_router = APIRouter(
    prefix="/news",
    tags=["News Management"]
)

# --- Placeholder Autentikasi ---
async def get_current_user():
    return {"user_id": "mock_user_123", "role": "admin"}


# --- Endpoint (Tidak ada perubahan di sini, semua sudah benar) ---

@news_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=SuccessResponseDTO[NewsResponseDTO]
)
def create_new_news(
    news_data: NewsCreateDTO,  # <--- INI BAGIAN PALING PENTING! Pastikan ini NewsCreateDTO
    current_user: dict = Depends(get_current_user)
) -> Any:
    author_id = current_user.get("user_id")
    created_news = news_service.create_news(news_data, author_id)
    return SuccessResponseDTO(
        message="Berita berhasil dibuat.",
        data=created_news
    )

@news_router.get(
    "/",
    response_model=SuccessResponseDTO[PaginatedResponseDTO[NewsSummaryDTO]]
)
def get_all_news(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    query: str | None = Query(None),
    sort_by: str = Query("date", enum=["date", "views", "likes", "title"]),
    sort_order: str = Query("desc", enum=["asc", "desc"]),
    category: str | None = Query(None),
    is_featured: bool | None = Query(None),
    is_published: bool | None = Query(True)
) -> Any:
    search_dto = NewsSearchDTO(query=query, sort_by=sort_by, sort_order=sort_order)
    filter_dto = NewsFilterDTO(
        category=category,
        is_featured=is_featured,
        is_published=is_published
    )
    paginated_result = news_service.get_news_list(page, limit, search_dto, filter_dto)
    return SuccessResponseDTO(
        message="Daftar berita berhasil diambil.",
        data=paginated_result
    )

@news_router.get(
    "/featured",
    response_model=SuccessResponseDTO[List[NewsSummaryDTO]], # Response berupa list, bukan paginasi
    summary="Get Featured News",
    description="Mengambil daftar berita yang ditandai sebagai unggulan (is_featured=true)."
)
def get_featured_news(
    limit: int = Query(5, ge=1, le=20, description="Jumlah berita yang ingin ditampilkan")
) -> Any:
    # Menggunakan DTO yang sudah ada untuk filtering dan searching
    search_dto = NewsSearchDTO(sort_by="date", sort_order="desc") # Urutkan berdasarkan tanggal terbaru
    filter_dto = NewsFilterDTO(
        is_featured=True, # <-- Filter utama
        is_published=True # <-- Pastikan hanya yang sudah terbit
    )
    
    # Memanggil service list dengan pagination di-nonaktifkan (page=1, limit sesuai input)
    paginated_result = news_service.get_news_list(1, limit, search_dto, filter_dto)
    
    return SuccessResponseDTO(
        message="Daftar berita unggulan berhasil diambil.",
        data=paginated_result.data # Hanya kembalikan list datanya
    )

@news_router.get(
    "/{identifier}",
    response_model=SuccessResponseDTO[NewsResponseDTO]
)
def get_single_news(identifier: str = Path(..., description="ID atau slug dari berita")) -> Any:
    news = news_service.get_news_by_id_or_slug(identifier)
    return SuccessResponseDTO(
        message="Detail berita berhasil diambil.",
        data=news
    )

@news_router.put(
    "/{news_id}",
    response_model=SuccessResponseDTO[NewsResponseDTO]
)
def update_existing_news(
    news_id: str,
    news_data: NewsUpdateDTO,
    current_user: dict = Depends(get_current_user)
) -> Any:
    user_id = current_user.get("user_id")
    updated_news = news_service.update_news(news_id, news_data, user_id)
    return SuccessResponseDTO(
        message="Berita berhasil diperbarui.",
        data=updated_news
    )

@news_router.delete(
    "/{news_id}",
    response_model=SuccessResponseDTO,
    status_code=status.HTTP_200_OK
)
def delete_single_news(
    news_id: str,
    current_user: dict = Depends(get_current_user)
) -> Any:
    user_id = current_user.get("user_id")
    news_service.delete_news(news_id, user_id)
    return SuccessResponseDTO(
        message="Berita berhasil dihapus."
    )

@news_router.patch(
    "/{news_id}/featured",
    response_model=SuccessResponseDTO[NewsResponseDTO],
    summary="Update Status Unggulan Berita",
    description="Endpoint khusus untuk mengubah status `is_featured` sebuah berita menjadi `true` atau `false`."
)
def feature_single_news(
    news_id: str = Path(..., description="ID dari berita yang akan diubah"),
    feature_data: NewsFeatureDTO = Body(...),
    current_user: dict = Depends(get_current_user)
) -> Any:
    """
    Mengubah status unggulan sebuah berita.
    - Kirim `{"is_featured": true}` untuk menjadikan berita sebagai unggulan.
    - Kirim `{"is_featured": false}` untuk menghapus status unggulan.
    """
    user_id = current_user.get("user_id")
    featured_news = news_service.feature_news(news_id, feature_data, user_id)
    
    status_text = "dijadikan" if feature_data.is_featured else "dihapus dari"
    return SuccessResponseDTO(
        message=f"Berita berhasil {status_text} unggulan.",
        data=featured_news
    )
