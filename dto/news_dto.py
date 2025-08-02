from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .base_dto import BaseResponseDTO, SearchDTO, FilterDTO

class NewsCreateDTO(BaseModel):
    """DTO untuk membuat berita baru"""
    title: str = Field(..., min_length=10, max_length=200, description="Judul berita")
    content: str = Field(..., min_length=100, description="Isi berita")
    excerpt: Optional[str] = Field(None, max_length=500, description="Ringkasan berita")
    category: str = Field(..., description="Kategori berita")
    tags: List[str] = Field(default=[], description="Tag berita")
    featured_image: Optional[str] = Field(None, description="URL gambar utama")
    images: List[str] = Field(default=[], description="URL gambar tambahan")
    pesantren_id: Optional[str] = Field(None, description="ID pesantren terkait")
    is_featured: bool = Field(False, description="Berita unggulan")
    publish_date: Optional[datetime] = Field(None, description="Tanggal publikasi")
    meta_title: Optional[str] = Field(None, max_length=60, description="Meta title untuk SEO")
    meta_description: Optional[str] = Field(None, max_length=160, description="Meta description untuk SEO")
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = [
            'pendidikan', 'kegiatan', 'prestasi', 'pengumuman', 
            'tips', 'beasiswa', 'event', 'alumni', 'umum'
        ]
        if v not in valid_categories:
            raise ValueError(f'Kategori {v} tidak valid')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maksimal 10 tag per berita')
        return v
    
    @validator('publish_date')
    def validate_publish_date(cls, v):
        if v and v < datetime.now():
            raise ValueError('Tanggal publikasi tidak boleh di masa lalu')
        return v

class NewsUpdateDTO(BaseModel):
    """DTO untuk update berita"""
    title: Optional[str] = Field(None, min_length=10, max_length=200, description="Judul berita")
    content: Optional[str] = Field(None, min_length=100, description="Isi berita")
    excerpt: Optional[str] = Field(None, max_length=500, description="Ringkasan berita")
    category: Optional[str] = Field(None, description="Kategori berita")
    tags: Optional[List[str]] = Field(None, description="Tag berita")
    featured_image: Optional[str] = Field(None, description="URL gambar utama")
    images: Optional[List[str]] = Field(None, description="URL gambar tambahan")
    pesantren_id: Optional[str] = Field(None, description="ID pesantren terkait")
    is_featured: Optional[bool] = Field(None, description="Berita unggulan")
    is_published: Optional[bool] = Field(None, description="Status publikasi")
    publish_date: Optional[datetime] = Field(None, description="Tanggal publikasi")
    meta_title: Optional[str] = Field(None, max_length=60, description="Meta title untuk SEO")
    meta_description: Optional[str] = Field(None, max_length=160, description="Meta description untuk SEO")
    
    @validator('category')
    def validate_category(cls, v):
        if v:
            valid_categories = [
                'pendidikan', 'kegiatan', 'prestasi', 'pengumuman', 
                'tips', 'beasiswa', 'event', 'alumni', 'umum'
            ]
            if v not in valid_categories:
                raise ValueError(f'Kategori {v} tidak valid')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maksimal 10 tag per berita')
        return v

class NewsResponseDTO(BaseResponseDTO):
    """DTO untuk response berita"""
    title: str = Field(description="Judul berita")
    slug: str = Field(description="Slug berita")
    content: str = Field(description="Isi berita")
    excerpt: str = Field(description="Ringkasan berita")
    category: str = Field(description="Kategori berita")
    tags: List[str] = Field(description="Tag berita")
    featured_image: Optional[str] = Field(description="URL gambar utama")
    images: List[str] = Field(description="URL gambar tambahan")
    author_id: str = Field(description="ID penulis")
    author_name: str = Field(description="Nama penulis")
    author_avatar: Optional[str] = Field(description="Avatar penulis")
    pesantren_id: Optional[str] = Field(description="ID pesantren terkait")
    pesantren_name: Optional[str] = Field(description="Nama pesantren terkait")
    is_published: bool = Field(description="Status publikasi")
    is_featured: bool = Field(description="Berita unggulan")
    publish_date: Optional[datetime] = Field(description="Tanggal publikasi")
    views: int = Field(description="Jumlah views")
    likes: int = Field(description="Jumlah likes")
    dislikes: int = Field(description="Jumlah dislikes")
    reading_time: int = Field(description="Estimasi waktu baca (menit)")
    meta_title: Optional[str] = Field(description="Meta title untuk SEO")
    meta_description: Optional[str] = Field(description="Meta description untuk SEO")
    
class NewsSummaryDTO(BaseModel):
    """DTO untuk summary berita (untuk list)"""
    id: str = Field(description="ID berita")
    title: str = Field(description="Judul berita")
    slug: str = Field(description="Slug berita")
    excerpt: str = Field(description="Ringkasan berita")
    category: str = Field(description="Kategori berita")
    tags: List[str] = Field(description="Tag berita")
    featured_image: Optional[str] = Field(description="URL gambar utama")
    author_name: str = Field(description="Nama penulis")
    author_avatar: Optional[str] = Field(description="Avatar penulis")
    pesantren_name: Optional[str] = Field(description="Nama pesantren terkait")
    is_featured: bool = Field(description="Berita unggulan")
    publish_date: Optional[datetime] = Field(description="Tanggal publikasi")
    views: int = Field(description="Jumlah views")
    likes: int = Field(description="Jumlah likes")
    reading_time: int = Field(description="Estimasi waktu baca (menit)")
    created_at: datetime = Field(description="Tanggal dibuat")

class NewsSearchDTO(SearchDTO):
    """DTO untuk pencarian berita"""
    category: Optional[str] = Field(None, description="Filter kategori")
    tags: Optional[List[str]] = Field(None, description="Filter tag")
    author_id: Optional[str] = Field(None, description="Filter penulis")
    pesantren_id: Optional[str] = Field(None, description="Filter pesantren")
    is_published: Optional[bool] = Field(None, description="Filter status publikasi")
    is_featured: Optional[bool] = Field(None, description="Filter berita unggulan")
    publish_date_from: Optional[datetime] = Field(None, description="Filter tanggal publikasi dari")
    publish_date_to: Optional[datetime] = Field(None, description="Filter tanggal publikasi sampai")
    
class NewsFilterDTO(FilterDTO):
    """DTO untuk filter berita"""
    category: Optional[str] = Field(None, description="Filter kategori")
    tags: Optional[List[str]] = Field(None, description="Filter tag")
    author_id: Optional[str] = Field(None, description="Filter penulis")
    pesantren_id: Optional[str] = Field(None, description="Filter pesantren")
    is_published: Optional[bool] = Field(None, description="Filter status publikasi")
    is_featured: Optional[bool] = Field(None, description="Filter berita unggulan")
    publish_date_from: Optional[datetime] = Field(None, description="Filter tanggal publikasi dari")
    publish_date_to: Optional[datetime] = Field(None, description="Filter tanggal publikasi sampai")
    min_views: Optional[int] = Field(None, ge=0, description="Minimum views")
    max_views: Optional[int] = Field(None, ge=0, description="Maksimum views")
    min_likes: Optional[int] = Field(None, ge=0, description="Minimum likes")
    has_featured_image: Optional[bool] = Field(None, description="Filter ada gambar utama")
    reading_time_from: Optional[int] = Field(None, ge=0, description="Waktu baca dari (menit)")
    reading_time_to: Optional[int] = Field(None, ge=0, description="Waktu baca sampai (menit)")

class NewsStatsDTO(BaseModel):
    """DTO untuk statistik berita"""
    total_news: int = Field(description="Total berita")
    published_news: int = Field(description="Berita terpublikasi")
    draft_news: int = Field(description="Berita draft")
    featured_news: int = Field(description="Berita unggulan")
    total_views: int = Field(description="Total views")
    total_likes: int = Field(description="Total likes")
    news_today: int = Field(description="Berita hari ini")
    news_this_week: int = Field(description="Berita minggu ini")
    news_this_month: int = Field(description="Berita bulan ini")
    by_category: Dict[str, int] = Field(description="Statistik per kategori")
    by_author: Dict[str, int] = Field(description="Statistik per penulis")
    by_pesantren: Dict[str, int] = Field(description="Statistik per pesantren")
    trending_tags: List[Dict[str, Any]] = Field(description="Tag trending")
    popular_news: List[Dict[str, Any]] = Field(description="Berita populer")
    
class NewsLikeDTO(BaseModel):
    """DTO untuk like/dislike berita"""
    action: str = Field(..., description="Aksi like/dislike")
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ['like', 'dislike', 'remove']
        if v not in valid_actions:
            raise ValueError(f'Aksi {v} tidak valid')
        return v

class NewsPublishDTO(BaseModel):
    """DTO untuk publikasi berita"""
    is_published: bool = Field(..., description="Status publikasi")
    publish_date: Optional[datetime] = Field(None, description="Tanggal publikasi")
    
    @validator('publish_date')
    def validate_publish_date(cls, v, values):
        if values.get('is_published') and v and v < datetime.now():
            raise ValueError('Tanggal publikasi tidak boleh di masa lalu')
        return v

class NewsAnalyticsDTO(BaseModel):
    """DTO untuk analytics berita"""
    news_id: str = Field(description="ID berita")
    title: str = Field(description="Judul berita")
    total_views: int = Field(description="Total views")
    unique_views: int = Field(description="Unique views")
    total_likes: int = Field(description="Total likes")
    total_dislikes: int = Field(description="Total dislikes")
    engagement_rate: float = Field(description="Tingkat engagement (%)")
    view_trend: List[Dict[str, Any]] = Field(description="Trend views")
    traffic_sources: Dict[str, int] = Field(description="Sumber traffic")
    reader_demographics: Dict[str, Any] = Field(description="Demografi pembaca")
    reading_completion_rate: float = Field(description="Tingkat penyelesaian baca (%)")
    social_shares: Dict[str, int] = Field(description="Social media shares")
    
class NewsBulkActionDTO(BaseModel):
    """DTO untuk aksi bulk pada berita"""
    news_ids: List[str] = Field(..., min_items=1, description="ID berita")
    action: str = Field(..., description="Aksi yang dilakukan")
    value: Optional[Any] = Field(None, description="Nilai untuk aksi")
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ['publish', 'unpublish', 'feature', 'unfeature', 'delete', 'change_category']
        if v not in valid_actions:
            raise ValueError(f'Aksi {v} tidak valid')
        return v
    
    @validator('news_ids')
    def validate_news_ids(cls, v):
        if len(v) > 50:
            raise ValueError('Maksimal 50 berita per aksi bulk')
        return v

class NewsRelatedDTO(BaseModel):
    """DTO untuk berita terkait"""
    id: str = Field(description="ID berita")
    title: str = Field(description="Judul berita")
    slug: str = Field(description="Slug berita")
    excerpt: str = Field(description="Ringkasan berita")
    featured_image: Optional[str] = Field(description="URL gambar utama")
    category: str = Field(description="Kategori berita")
    publish_date: Optional[datetime] = Field(description="Tanggal publikasi")
    reading_time: int = Field(description="Estimasi waktu baca (menit)")
    similarity_score: float = Field(description="Skor kemiripan")

class NewsSEODTO(BaseModel):
    """DTO untuk SEO berita"""
    meta_title: Optional[str] = Field(None, max_length=60, description="Meta title")
    meta_description: Optional[str] = Field(None, max_length=160, description="Meta description")
    meta_keywords: Optional[List[str]] = Field(None, description="Meta keywords")
    canonical_url: Optional[str] = Field(None, description="Canonical URL")
    og_title: Optional[str] = Field(None, description="Open Graph title")
    og_description: Optional[str] = Field(None, description="Open Graph description")
    og_image: Optional[str] = Field(None, description="Open Graph image")
    twitter_title: Optional[str] = Field(None, description="Twitter title")
    twitter_description: Optional[str] = Field(None, description="Twitter description")
    twitter_image: Optional[str] = Field(None, description="Twitter image")
    
    @validator('meta_keywords')
    def validate_meta_keywords(cls, v):
        if v and len(v) > 10:
            raise ValueError('Maksimal 10 meta keywords')
        return v