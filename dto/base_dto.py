from typing import Any, Dict, List, Optional, Generic, TypeVar
from pydantic import BaseModel, Field
from datetime import datetime

T = TypeVar('T')

class BaseResponseDTO(BaseModel):
    """Base DTO untuk semua response"""
    id: Optional[str] = Field(None, description="ID dokumen")
    created_at: Optional[datetime] = Field(None, description="Waktu pembuatan")
    updated_at: Optional[datetime] = Field(None, description="Waktu update terakhir")
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class PaginationDTO(BaseModel):
    """DTO untuk pagination"""
    page: int = Field(1, ge=1, description="Nomor halaman")
    limit: int = Field(10, ge=1, le=100, description="Jumlah item per halaman")
    total: Optional[int] = Field(None, description="Total item")
    total_pages: Optional[int] = Field(None, description="Total halaman")
    has_next: Optional[bool] = Field(None, description="Ada halaman selanjutnya")
    has_prev: Optional[bool] = Field(None, description="Ada halaman sebelumnya")

class PaginatedResponseDTO(BaseModel, Generic[T]):
    """DTO untuk response dengan pagination"""
    data: List[T] = Field(description="Data hasil query")
    pagination: PaginationDTO = Field(description="Informasi pagination")
    
class SuccessResponseDTO(BaseModel, Generic[T]):
    """DTO untuk response sukses"""
    success: bool = Field(True, description="Status sukses")
    message: str = Field(description="Pesan response")
    data: Optional[T] = Field(None, description="Data response")
    timestamp: datetime = Field(default_factory=datetime.now, description="Waktu response")
    
class ErrorResponseDTO(BaseModel):
    """DTO untuk response error"""
    success: bool = Field(False, description="Status sukses")
    error: str = Field(description="Pesan error")
    error_code: Optional[str] = Field(None, description="Kode error")
    details: Optional[Dict[str, Any]] = Field(None, description="Detail error")
    timestamp: datetime = Field(default_factory=datetime.now, description="Waktu response")

class ValidationErrorDTO(BaseModel):
    """DTO untuk validation error"""
    field: str = Field(description="Field yang error")
    message: str = Field(description="Pesan error")
    value: Optional[Any] = Field(None, description="Nilai yang error")

class ValidationErrorResponseDTO(ErrorResponseDTO):
    """DTO untuk response validation error"""
    validation_errors: List[ValidationErrorDTO] = Field(description="Detail validation errors")

class SearchDTO(BaseModel):
    """Base DTO untuk pencarian"""
    query: Optional[str] = Field(None, description="Query pencarian")
    page: int = Field(1, ge=1, description="Nomor halaman")
    limit: int = Field(10, ge=1, le=100, description="Jumlah item per halaman")
    sort_by: Optional[str] = Field(None, description="Field untuk sorting")
    sort_order: Optional[str] = Field("desc", regex="^(asc|desc)$", description="Urutan sorting")

class FilterDTO(BaseModel):
    """Base DTO untuk filter"""
    date_from: Optional[datetime] = Field(None, description="Filter tanggal dari")
    date_to: Optional[datetime] = Field(None, description="Filter tanggal sampai")
    status: Optional[str] = Field(None, description="Filter status")
    
class StatsDTO(BaseModel):
    """DTO untuk statistik"""
    total: int = Field(description="Total item")
    active: Optional[int] = Field(None, description="Item aktif")
    inactive: Optional[int] = Field(None, description="Item tidak aktif")
    growth_rate: Optional[float] = Field(None, description="Tingkat pertumbuhan (%)")
    period: Optional[str] = Field(None, description="Periode statistik")

class LocationDTO(BaseModel):
    """DTO untuk lokasi"""
    province: Optional[str] = Field(None, description="Provinsi")
    city: Optional[str] = Field(None, description="Kota/Kabupaten")
    district: Optional[str] = Field(None, description="Kecamatan")
    address: Optional[str] = Field(None, description="Alamat lengkap")
    postal_code: Optional[str] = Field(None, description="Kode pos")
    latitude: Optional[float] = Field(None, description="Latitude")
    longitude: Optional[float] = Field(None, description="Longitude")

class ContactDTO(BaseModel):
    """DTO untuk kontak"""
    phone: Optional[str] = Field(None, description="Nomor telepon")
    email: Optional[str] = Field(None, description="Email")
    website: Optional[str] = Field(None, description="Website")
    whatsapp: Optional[str] = Field(None, description="WhatsApp")
    instagram: Optional[str] = Field(None, description="Instagram")
    facebook: Optional[str] = Field(None, description="Facebook")