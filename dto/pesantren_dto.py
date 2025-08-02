from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .base_dto import BaseResponseDTO, SearchDTO, FilterDTO, LocationDTO, ContactDTO

class PesantrenCreateDTO(BaseModel):
    """DTO untuk membuat pesantren baru"""
    name: str = Field(..., min_length=3, max_length=200, description="Nama pesantren")
    description: str = Field(..., min_length=10, description="Deskripsi pesantren")
    location: LocationDTO = Field(..., description="Lokasi pesantren")
    contact: ContactDTO = Field(..., description="Kontak pesantren")
    programs: List[str] = Field(..., min_items=1, description="Program pendidikan")
    facilities: List[str] = Field(default=[], description="Fasilitas pesantren")
    curriculum: str = Field(..., description="Kurikulum yang digunakan")
    education_levels: List[str] = Field(..., min_items=1, description="Jenjang pendidikan")
    capacity: int = Field(..., gt=0, description="Kapasitas siswa")
    monthly_fee: float = Field(..., ge=0, description="Biaya bulanan")
    registration_fee: float = Field(..., ge=0, description="Biaya pendaftaran")
    other_fees: Dict[str, float] = Field(default={}, description="Biaya lainnya")
    images: List[str] = Field(default=[], description="URL gambar pesantren")
    video_url: Optional[str] = Field(None, description="URL video profil")
    established_year: int = Field(..., ge=1900, le=2024, description="Tahun berdiri")
    accreditation: Optional[str] = Field(None, description="Akreditasi")
    
    @validator('programs')
    def validate_programs(cls, v):
        valid_programs = [
            'Tahfidz', 'Kitab Kuning', 'Sains', 'Bahasa', 'Keterampilan',
            'Komputer', 'Olahraga', 'Seni', 'Entrepreneur'
        ]
        for program in v:
            if program not in valid_programs:
                raise ValueError(f'Program {program} tidak valid')
        return v
    
    @validator('education_levels')
    def validate_education_levels(cls, v):
        valid_levels = ['SD/MI', 'SMP/MTs', 'SMA/MA', 'SMK', 'Diniyah']
        for level in v:
            if level not in valid_levels:
                raise ValueError(f'Jenjang pendidikan {level} tidak valid')
        return v

class PesantrenUpdateDTO(BaseModel):
    """DTO untuk update pesantren"""
    name: Optional[str] = Field(None, min_length=3, max_length=200, description="Nama pesantren")
    description: Optional[str] = Field(None, min_length=10, description="Deskripsi pesantren")
    location: Optional[LocationDTO] = Field(None, description="Lokasi pesantren")
    contact: Optional[ContactDTO] = Field(None, description="Kontak pesantren")
    programs: Optional[List[str]] = Field(None, description="Program pendidikan")
    facilities: Optional[List[str]] = Field(None, description="Fasilitas pesantren")
    curriculum: Optional[str] = Field(None, description="Kurikulum yang digunakan")
    education_levels: Optional[List[str]] = Field(None, description="Jenjang pendidikan")
    capacity: Optional[int] = Field(None, gt=0, description="Kapasitas siswa")
    monthly_fee: Optional[float] = Field(None, ge=0, description="Biaya bulanan")
    registration_fee: Optional[float] = Field(None, ge=0, description="Biaya pendaftaran")
    other_fees: Optional[Dict[str, float]] = Field(None, description="Biaya lainnya")
    images: Optional[List[str]] = Field(None, description="URL gambar pesantren")
    video_url: Optional[str] = Field(None, description="URL video profil")
    established_year: Optional[int] = Field(None, ge=1900, le=2024, description="Tahun berdiri")
    accreditation: Optional[str] = Field(None, description="Akreditasi")
    is_featured: Optional[bool] = Field(None, description="Status unggulan")
    is_active: Optional[bool] = Field(None, description="Status aktif")

class PesantrenResponseDTO(BaseResponseDTO):
    """DTO untuk response pesantren"""
    name: str = Field(description="Nama pesantren")
    slug: str = Field(description="Slug pesantren")
    description: str = Field(description="Deskripsi pesantren")
    location: LocationDTO = Field(description="Lokasi pesantren")
    contact: ContactDTO = Field(description="Kontak pesantren")
    programs: List[str] = Field(description="Program pendidikan")
    facilities: List[str] = Field(description="Fasilitas pesantren")
    curriculum: str = Field(description="Kurikulum yang digunakan")
    education_levels: List[str] = Field(description="Jenjang pendidikan")
    capacity: int = Field(description="Kapasitas siswa")
    current_students: int = Field(description="Jumlah siswa saat ini")
    monthly_fee: float = Field(description="Biaya bulanan")
    registration_fee: float = Field(description="Biaya pendaftaran")
    other_fees: Dict[str, float] = Field(description="Biaya lainnya")
    images: List[str] = Field(description="URL gambar pesantren")
    video_url: Optional[str] = Field(description="URL video profil")
    established_year: int = Field(description="Tahun berdiri")
    accreditation: Optional[str] = Field(description="Akreditasi")
    rating: float = Field(description="Rating pesantren")
    total_reviews: int = Field(description="Total ulasan")
    is_featured: bool = Field(description="Status unggulan")
    is_active: bool = Field(description="Status aktif")
    views: int = Field(description="Jumlah views")
    
class PesantrenSummaryDTO(BaseModel):
    """DTO untuk summary pesantren (untuk list)"""
    id: str = Field(description="ID pesantren")
    name: str = Field(description="Nama pesantren")
    slug: str = Field(description="Slug pesantren")
    location: Dict[str, str] = Field(description="Lokasi singkat")
    monthly_fee: float = Field(description="Biaya bulanan")
    rating: float = Field(description="Rating pesantren")
    total_reviews: int = Field(description="Total ulasan")
    is_featured: bool = Field(description="Status unggulan")
    images: List[str] = Field(description="URL gambar pesantren")
    programs: List[str] = Field(description="Program pendidikan")
    education_levels: List[str] = Field(description="Jenjang pendidikan")

class PesantrenSearchDTO(SearchDTO):
    """DTO untuk pencarian pesantren"""
    location: Optional[str] = Field(None, description="Filter lokasi")
    programs: Optional[List[str]] = Field(None, description="Filter program")
    education_levels: Optional[List[str]] = Field(None, description="Filter jenjang pendidikan")
    min_fee: Optional[float] = Field(None, ge=0, description="Biaya minimum")
    max_fee: Optional[float] = Field(None, ge=0, description="Biaya maksimum")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Rating minimum")
    curriculum: Optional[str] = Field(None, description="Filter kurikulum")
    facilities: Optional[List[str]] = Field(None, description="Filter fasilitas")
    is_featured: Optional[bool] = Field(None, description="Filter unggulan")
    
class PesantrenFilterDTO(FilterDTO):
    """DTO untuk filter pesantren"""
    province: Optional[str] = Field(None, description="Filter provinsi")
    city: Optional[str] = Field(None, description="Filter kota")
    programs: Optional[List[str]] = Field(None, description="Filter program")
    education_levels: Optional[List[str]] = Field(None, description="Filter jenjang pendidikan")
    curriculum: Optional[str] = Field(None, description="Filter kurikulum")
    min_capacity: Optional[int] = Field(None, ge=0, description="Kapasitas minimum")
    max_capacity: Optional[int] = Field(None, ge=0, description="Kapasitas maksimum")
    min_fee: Optional[float] = Field(None, ge=0, description="Biaya minimum")
    max_fee: Optional[float] = Field(None, ge=0, description="Biaya maksimum")
    min_rating: Optional[float] = Field(None, ge=0, le=5, description="Rating minimum")
    has_facilities: Optional[List[str]] = Field(None, description="Harus memiliki fasilitas")
    is_featured: Optional[bool] = Field(None, description="Filter unggulan")
    is_active: Optional[bool] = Field(None, description="Filter aktif")
    established_year_from: Optional[int] = Field(None, description="Tahun berdiri dari")
    established_year_to: Optional[int] = Field(None, description="Tahun berdiri sampai")

class PesantrenStatsDTO(BaseModel):
    """DTO untuk statistik pesantren"""
    total_pesantren: int = Field(description="Total pesantren")
    active_pesantren: int = Field(description="Pesantren aktif")
    featured_pesantren: int = Field(description="Pesantren unggulan")
    total_students: int = Field(description="Total siswa")
    average_rating: float = Field(description="Rating rata-rata")
    total_reviews: int = Field(description="Total ulasan")
    by_province: Dict[str, int] = Field(description="Statistik per provinsi")
    by_program: Dict[str, int] = Field(description="Statistik per program")
    by_education_level: Dict[str, int] = Field(description="Statistik per jenjang")
    fee_range: Dict[str, float] = Field(description="Range biaya")
    
class PesantrenLocationStatsDTO(BaseModel):
    """DTO untuk statistik lokasi pesantren"""
    provinces: List[str] = Field(description="Daftar provinsi")
    cities_by_province: Dict[str, List[str]] = Field(description="Kota per provinsi")
    total_by_province: Dict[str, int] = Field(description="Total pesantren per provinsi")
    
class PesantrenProgramStatsDTO(BaseModel):
    """DTO untuk statistik program pesantren"""
    available_programs: List[str] = Field(description="Program yang tersedia")
    program_counts: Dict[str, int] = Field(description="Jumlah pesantren per program")
    popular_programs: List[Dict[str, Any]] = Field(description="Program populer")