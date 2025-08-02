from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .base_dto import BaseResponseDTO, SearchDTO, FilterDTO

class ReviewCreateDTO(BaseModel):
    """DTO untuk membuat review baru"""
    pesantren_id: str = Field(..., description="ID pesantren")
    rating: int = Field(..., ge=1, le=5, description="Rating (1-5)")
    title: str = Field(..., min_length=5, max_length=100, description="Judul review")
    content: str = Field(..., min_length=10, max_length=2000, description="Isi review")
    pros: Optional[List[str]] = Field(None, description="Kelebihan")
    cons: Optional[List[str]] = Field(None, description="Kekurangan")
    recommendation: Optional[str] = Field(None, description="Rekomendasi")
    anonymous: bool = Field(False, description="Review anonim")
    
    @validator('pros')
    def validate_pros(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maksimal 10 poin kelebihan')
        return v
    
    @validator('cons')
    def validate_cons(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maksimal 10 poin kekurangan')
        return v

class ReviewUpdateDTO(BaseModel):
    """DTO untuk update review"""
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating (1-5)")
    title: Optional[str] = Field(None, min_length=5, max_length=100, description="Judul review")
    content: Optional[str] = Field(None, min_length=10, max_length=2000, description="Isi review")
    pros: Optional[List[str]] = Field(None, description="Kelebihan")
    cons: Optional[List[str]] = Field(None, description="Kekurangan")
    recommendation: Optional[str] = Field(None, description="Rekomendasi")
    anonymous: Optional[bool] = Field(None, description="Review anonim")
    
    @validator('pros')
    def validate_pros(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maksimal 10 poin kelebihan')
        return v
    
    @validator('cons')
    def validate_cons(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maksimal 10 poin kekurangan')
        return v

class ReviewResponseDTO(BaseResponseDTO):
    """DTO untuk response review"""
    pesantren_id: str = Field(description="ID pesantren")
    pesantren_name: str = Field(description="Nama pesantren")
    user_id: str = Field(description="ID user")
    user_name: str = Field(description="Nama user")
    user_avatar: Optional[str] = Field(description="Avatar user")
    rating: int = Field(description="Rating (1-5)")
    title: str = Field(description="Judul review")
    content: str = Field(description="Isi review")
    pros: List[str] = Field(description="Kelebihan")
    cons: List[str] = Field(description="Kekurangan")
    recommendation: Optional[str] = Field(description="Rekomendasi")
    anonymous: bool = Field(description="Review anonim")
    helpful_count: int = Field(description="Jumlah helpful")
    report_count: int = Field(description="Jumlah laporan")
    is_verified: bool = Field(description="Review terverifikasi")
    is_moderated: bool = Field(description="Sudah dimoderasi")
    moderation_status: str = Field(description="Status moderasi")
    moderation_reason: Optional[str] = Field(description="Alasan moderasi")
    is_deleted: bool = Field(description="Status dihapus")
    
class ReviewSummaryDTO(BaseModel):
    """DTO untuk summary review (untuk list)"""
    id: str = Field(description="ID review")
    pesantren_id: str = Field(description="ID pesantren")
    pesantren_name: str = Field(description="Nama pesantren")
    user_name: str = Field(description="Nama user")
    user_avatar: Optional[str] = Field(description="Avatar user")
    rating: int = Field(description="Rating (1-5)")
    title: str = Field(description="Judul review")
    content_preview: str = Field(description="Preview isi review")
    helpful_count: int = Field(description="Jumlah helpful")
    anonymous: bool = Field(description="Review anonim")
    is_verified: bool = Field(description="Review terverifikasi")
    created_at: datetime = Field(description="Tanggal dibuat")

class ReviewSearchDTO(SearchDTO):
    """DTO untuk pencarian review"""
    pesantren_id: Optional[str] = Field(None, description="Filter pesantren")
    user_id: Optional[str] = Field(None, description="Filter user")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Filter rating")
    min_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating minimum")
    max_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating maksimum")
    is_verified: Optional[bool] = Field(None, description="Filter terverifikasi")
    moderation_status: Optional[str] = Field(None, description="Filter status moderasi")
    
class ReviewFilterDTO(FilterDTO):
    """DTO untuk filter review"""
    pesantren_id: Optional[str] = Field(None, description="Filter pesantren")
    user_id: Optional[str] = Field(None, description="Filter user")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Filter rating")
    min_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating minimum")
    max_rating: Optional[int] = Field(None, ge=1, le=5, description="Rating maksimum")
    is_verified: Optional[bool] = Field(None, description="Filter terverifikasi")
    is_moderated: Optional[bool] = Field(None, description="Filter sudah dimoderasi")
    moderation_status: Optional[str] = Field(None, description="Filter status moderasi")
    anonymous: Optional[bool] = Field(None, description="Filter anonim")
    has_pros: Optional[bool] = Field(None, description="Filter ada kelebihan")
    has_cons: Optional[bool] = Field(None, description="Filter ada kekurangan")
    has_recommendation: Optional[bool] = Field(None, description="Filter ada rekomendasi")
    min_helpful_count: Optional[int] = Field(None, ge=0, description="Minimum helpful count")
    is_deleted: Optional[bool] = Field(None, description="Filter status dihapus")

class ReviewStatsDTO(BaseModel):
    """DTO untuk statistik review"""
    total_reviews: int = Field(description="Total review")
    verified_reviews: int = Field(description="Review terverifikasi")
    pending_moderation: int = Field(description="Review pending moderasi")
    average_rating: float = Field(description="Rating rata-rata")
    rating_distribution: Dict[str, int] = Field(description="Distribusi rating")
    total_helpful: int = Field(description="Total helpful")
    total_reports: int = Field(description="Total laporan")
    reviews_today: int = Field(description="Review hari ini")
    reviews_this_week: int = Field(description="Review minggu ini")
    reviews_this_month: int = Field(description="Review bulan ini")
    
class ReviewModerationDTO(BaseModel):
    """DTO untuk moderasi review"""
    moderation_status: str = Field(..., description="Status moderasi")
    moderation_reason: Optional[str] = Field(None, description="Alasan moderasi")
    moderator_notes: Optional[str] = Field(None, description="Catatan moderator")
    
    @validator('moderation_status')
    def validate_moderation_status(cls, v):
        valid_statuses = ['approved', 'rejected', 'pending', 'flagged']
        if v not in valid_statuses:
            raise ValueError(f'Status moderasi {v} tidak valid')
        return v

class ReviewHelpfulDTO(BaseModel):
    """DTO untuk menandai review sebagai helpful"""
    helpful: bool = Field(..., description="Apakah helpful")
    
class ReviewReportDTO(BaseModel):
    """DTO untuk melaporkan review"""
    reason: str = Field(..., description="Alasan laporan")
    description: Optional[str] = Field(None, description="Deskripsi laporan")
    
    @validator('reason')
    def validate_reason(cls, v):
        valid_reasons = [
            'spam', 'inappropriate', 'fake', 'offensive', 
            'irrelevant', 'duplicate', 'other'
        ]
        if v not in valid_reasons:
            raise ValueError(f'Alasan laporan {v} tidak valid')
        return v

class ReviewAnalyticsDTO(BaseModel):
    """DTO untuk analytics review"""
    pesantren_id: str = Field(description="ID pesantren")
    total_reviews: int = Field(description="Total review")
    average_rating: float = Field(description="Rating rata-rata")
    rating_trend: List[Dict[str, Any]] = Field(description="Trend rating")
    review_volume_trend: List[Dict[str, Any]] = Field(description="Trend volume review")
    sentiment_analysis: Dict[str, float] = Field(description="Analisis sentimen")
    top_keywords: List[Dict[str, Any]] = Field(description="Kata kunci teratas")
    comparison_data: Optional[Dict[str, Any]] = Field(None, description="Data perbandingan")
    
class ReviewBulkActionDTO(BaseModel):
    """DTO untuk aksi bulk pada review"""
    review_ids: List[str] = Field(..., min_items=1, description="ID review")
    action: str = Field(..., description="Aksi yang dilakukan")
    reason: Optional[str] = Field(None, description="Alasan aksi")
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ['approve', 'reject', 'delete', 'verify', 'flag']
        if v not in valid_actions:
            raise ValueError(f'Aksi {v} tidak valid')
        return v
    
    @validator('review_ids')
    def validate_review_ids(cls, v):
        if len(v) > 100:
            raise ValueError('Maksimal 100 review per aksi bulk')
        return v