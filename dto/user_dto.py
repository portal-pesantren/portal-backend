import re

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator, EmailStr
from datetime import datetime
from .base_dto import BaseResponseDTO, SearchDTO, FilterDTO

class UserCreateDTO(BaseModel):
    """DTO untuk membuat user baru"""
    name: str = Field(..., min_length=2, max_length=100, description="Nama lengkap")
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., min_length=8, description="Password")
    phone: str = Field(..., min_length=10, max_length=20, description="Nomor telepon")
    role: str = Field("parent", description="Role user")
    profile_picture: Optional[str] = Field(None, description="URL foto profil")
    address: Optional[str] = Field(None, description="Alamat")
    date_of_birth: Optional[datetime] = Field(None, description="Tanggal lahir")
    gender: Optional[str] = Field(None, description="Jenis kelamin")
    occupation: Optional[str] = Field(None, description="Pekerjaan")
    
    @field_validator('role')
    def validate_role(cls, v):
        valid_roles = ['parent', 'admin', 'pesantren_admin', 'super_admin']
        if v not in valid_roles:
            raise ValueError(f'Role {v} tidak valid. Role yang valid: {", ".join(valid_roles)}')
        return v
    
    @field_validator('gender')
    def validate_gender(cls, v):
        if v and v not in ['male', 'female']:
            raise ValueError('Gender harus male atau female')
        return v
    
    @field_validator('phone')
    def validate_phone(cls, v):
        # Validasi format nomor telepon Indonesia
        # Hapus karakter non-digit kecuali + di awal untuk validasi
        print(f"DEBUG: Original phone: {v}")
        clean_phone = re.sub(r'[^\d\+]', '', v)
        print(f"DEBUG: Cleaned phone: {clean_phone}")
        pattern = r'^(\+62|62|0)[0-9]{9,13}$'
        match_result = re.match(pattern, clean_phone)
        print(f"DEBUG: Pattern match: {bool(match_result)}")
        if not match_result:
            raise ValueError(f'Format nomor telepon tidak valid. Input: {v}, Cleaned: {clean_phone}')
        return v

class ProfileUpdateDTO(BaseModel):
    bio: Optional[str] = Field(None, description="Biografi singkat user")
    location: Optional[str] = Field(None, description="Lokasi user")
    children_count: Optional[int] = Field(None, ge=0, description="Jumlah anak")

class UserUpdateDTO(BaseModel):
    """DTO untuk update user"""
    name: Optional[str] = Field(None, min_length=2, max_length=100, description="Nama lengkap")
    phone: Optional[str] = Field(None, min_length=10, max_length=20, description="Nomor telepon")
    profile_picture: Optional[str] = Field(None, description="URL foto profil")
    address: Optional[str] = Field(None, description="Alamat")
    date_of_birth: Optional[datetime] = Field(None, description="Tanggal lahir")
    gender: Optional[str] = Field(None, description="Jenis kelamin")
    occupation: Optional[str] = Field(None, description="Pekerjaan")
    is_active: Optional[bool] = Field(None, description="Status aktif")
    profile: Optional[ProfileUpdateDTO] = Field(None, description="Data profil user")

    
    @field_validator('gender')
    def validate_gender(cls, v):
        if v and v not in ['male', 'female']:
            raise ValueError('Gender harus male atau female')
        return v
    
    @field_validator('phone')
    def validate_phone(cls, v):
        if v:
            # Hapus karakter non-digit kecuali + di awal untuk validasi
            print(f"DEBUG UserUpdate: Original phone: {v}")
            clean_phone = re.sub(r'[^\d\+]', '', v)
            print(f"DEBUG UserUpdate: Cleaned phone: {clean_phone}")
            pattern = r'^(\+62|62|0)[0-9]{9,13}$'
            match_result = re.match(pattern, clean_phone)
            print(f"DEBUG UserUpdate: Pattern match: {bool(match_result)}")
            if not match_result:
                raise ValueError(f'Format nomor telepon tidak valid. Input: {v}, Cleaned: {clean_phone}')
            # Return the cleaned phone number
            return clean_phone
        return v

class UserPasswordUpdateDTO(BaseModel):
    """DTO untuk update password"""
    current_password: str = Field(..., description="Password saat ini")
    new_password: str = Field(..., min_length=8, description="Password baru")
    confirm_password: str = Field(..., description="Konfirmasi password baru")
    
    @field_validator('confirm_password')
    def validate_password_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Konfirmasi password tidak cocok')
        return v

class RefreshTokenDTO(BaseModel):
    """DTO untuk refresh token"""
    refresh_token: str = Field(..., description="Refresh token")

class TokenVerificationDTO(BaseModel):
    """DTO untuk verifikasi token"""
    token: str = Field(..., description="JWT token yang akan diverifikasi")

class TokenResponseDTO(BaseModel):
    """DTO untuk response token"""
    access_token: str = Field(..., description="Access token")
    expires_in: int = Field(..., description="Waktu kedaluwarsa dalam detik")
    token_type: str = Field(default="Bearer", description="Tipe token")

class TokenVerificationResponseDTO(BaseModel):
    """DTO untuk response verifikasi token"""
    valid: bool = Field(..., description="Status validitas token")
    user: Optional["UserProfileDTO"] = Field(None, description="Data user jika token valid")
    error: Optional[str] = Field(None, description="Pesan error jika token tidak valid")
    
class SearchDTO(BaseModel):
    query: Optional[str] = Field(None, description="Kata kunci pencarian umum")
    sort_by: Optional[str] = Field(None, description="Field untuk sorting")
    sort_order: Optional[str] = Field("desc", pattern="^(asc|desc)$", description="Urutan sorting")

class UserLoginDTO(BaseModel):
    """DTO untuk login user"""
    email: EmailStr = Field(..., description="Email")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Ingat saya")

class UserResponseDTO(BaseResponseDTO):
    """DTO untuk response user"""
    name: str = Field(description="Nama lengkap")
    email: str = Field(description="Email")
    phone: Optional[str] = Field(default=None, description="Nomor telepon")
    role: str = Field(description="Role user")
    profile_picture: Optional[str] = Field(default=None, description="URL foto profil")
    address: Optional[str] = Field(default=None, description="Alamat")
    date_of_birth: Optional[datetime] = Field(default=None, description="Tanggal lahir")
    gender: Optional[str] = Field(default=None, description="Jenis kelamin")
    occupation: Optional[str] = Field(default=None, description="Pekerjaan")
    is_active: bool = Field(description="Status aktif")
    is_verified: Optional[bool] = Field(default=False, description="Status verifikasi")
    email_verified: Optional[bool] = Field(default=False, description="Email terverifikasi")
    phone_verified: Optional[bool] = Field(default=False, description="Telepon terverifikasi")
    last_login: Optional[datetime] = Field(default=None, description="Login terakhir")
    login_count: Optional[int] = Field(default=0, description="Jumlah login")
    
class UserProfileDTO(BaseModel):
    """DTO untuk profil user (tanpa data sensitif)"""
    id: str = Field(description="ID user")
    name: str = Field(description="Nama lengkap")
    email: str = Field(description="Email")
    phone: Optional[str] = Field(default=None, description="Nomor telepon")
    role: str = Field(description="Role user")
    profile_picture: Optional[str] = Field(default=None, description="URL foto profil")
    is_active: bool = Field(description="Status aktif")
    is_verified: bool = Field(description="Status verifikasi")
    created_at: datetime = Field(description="Tanggal bergabung")
    last_login: Optional[datetime] = Field(default=None, description="Login terakhir")

class UserPaginatedResponseDTO(BaseModel):
    """DTO untuk response paginasi daftar user"""
    data: List[UserProfileDTO]
    total: int
    page: int
    limit: int

class UserSearchDTO(SearchDTO):
    """DTO untuk pencarian user"""
    role: Optional[str] = Field(None, description="Filter role")
    is_active: Optional[bool] = Field(None, description="Filter status aktif")
    is_verified: Optional[bool] = Field(None, description="Filter status verifikasi")
    email_verified: Optional[bool] = Field(None, description="Filter email terverifikasi")
    phone_verified: Optional[bool] = Field(None, description="Filter telepon terverifikasi")
    gender: Optional[str] = Field(None, description="Filter gender")
    
class UserFilterDTO(FilterDTO):
    """DTO untuk filter user"""
    role: Optional[str] = Field(None, description="Filter role")
    is_active: Optional[bool] = Field(None, description="Filter status aktif")
    is_verified: Optional[bool] = Field(None, description="Filter status verifikasi")
    email_verified: Optional[bool] = Field(None, description="Filter email terverifikasi")
    phone_verified: Optional[bool] = Field(None, description="Filter telepon terverifikasi")
    gender: Optional[str] = Field(None, description="Filter gender")
    age_from: Optional[int] = Field(None, ge=0, description="Umur dari")
    age_to: Optional[int] = Field(None, ge=0, description="Umur sampai")
    last_login_from: Optional[datetime] = Field(None, description="Login terakhir dari")
    last_login_to: Optional[datetime] = Field(None, description="Login terakhir sampai")

class UserStatsDTO(BaseModel):
    """DTO untuk statistik user"""
    total_users: int = Field(description="Total user")
    active_users: int = Field(description="User aktif")
    verified_users: int = Field(description="User terverifikasi")
    new_users_today: int = Field(description="User baru hari ini")
    new_users_this_week: int = Field(description="User baru minggu ini")
    new_users_this_month: int = Field(description="User baru bulan ini")
    by_role: Dict[str, int] = Field(description="Statistik per role")
    by_gender: Dict[str, int] = Field(description="Statistik per gender")
    login_stats: Dict[str, int] = Field(description="Statistik login")
    
class UserLoginResponseDTO(BaseModel):
    """DTO untuk response login"""
    user: "UserProfileDTO" = Field(description="Data user")
    access_token: str = Field(description="Access token")
    refresh_token: str = Field(description="Refresh token")
    token_type: str = Field("bearer", description="Tipe token")
    expires_in: int = Field(description="Waktu expired token (detik)")
    
class UserRegistrationDTO(UserCreateDTO):
    """DTO untuk registrasi user"""
    confirm_password: str = Field(..., description="Konfirmasi password")
    terms_accepted: bool = Field(..., description="Menyetujui syarat dan ketentuan")
    
    @model_validator(mode='after')
    def validate_password_match(self):
        if self.password != self.confirm_password:
            raise ValueError('Konfirmasi password tidak cocok')
        return self
    
    @field_validator('terms_accepted')
    def validate_terms(cls, v):
        if not v:
            raise ValueError('Harus menyetujui syarat dan ketentuan')
        return v

class UserVerificationDTO(BaseModel):
    """DTO untuk verifikasi user"""
    verification_code: str = Field(..., min_length=6, max_length=6, description="Kode verifikasi")
    verification_type: str = Field(..., description="Tipe verifikasi")
    
    @field_validator('verification_type')
    def validate_verification_type(cls, v):
        valid_types = ['email', 'phone', 'password_reset']
        if v not in valid_types:
            raise ValueError(f'Tipe verifikasi {v} tidak valid')
        return v

class UserForgotPasswordDTO(BaseModel):
    """DTO untuk forgot password"""
    email: EmailStr = Field(..., description="Email")
    
class UserResetPasswordDTO(BaseModel):
    """DTO untuk reset password"""
    reset_token: str = Field(..., description="Token reset password")
    new_password: str = Field(..., min_length=8, description="Password baru")
    confirm_password: str = Field(..., description="Konfirmasi password baru")
    
    @field_validator('confirm_password')
    def validate_password_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Konfirmasi password tidak cocok')
        return v