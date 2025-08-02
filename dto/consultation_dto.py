from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from .base_dto import BaseResponseDTO, SearchDTO, FilterDTO

class ConsultationCreateDTO(BaseModel):
    """DTO untuk membuat konsultasi baru"""
    pesantren_id: str = Field(..., description="ID pesantren")
    subject: str = Field(..., min_length=5, max_length=200, description="Subjek konsultasi")
    message: str = Field(..., min_length=10, max_length=2000, description="Pesan konsultasi")
    category: str = Field(..., description="Kategori konsultasi")
    priority: str = Field("normal", description="Prioritas konsultasi")
    contact_preference: str = Field("email", description="Preferensi kontak")
    preferred_time: Optional[str] = Field(None, description="Waktu yang diinginkan")
    student_info: Optional[Dict[str, Any]] = Field(None, description="Informasi siswa")
    attachments: List[str] = Field(default=[], description="URL lampiran")
    
    @validator('category')
    def validate_category(cls, v):
        valid_categories = [
            'pendaftaran', 'biaya', 'program', 'fasilitas', 'kurikulum',
            'kehidupan_santri', 'alumni', 'beasiswa', 'umum', 'lainnya'
        ]
        if v not in valid_categories:
            raise ValueError(f'Kategori {v} tidak valid')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        if v not in valid_priorities:
            raise ValueError(f'Prioritas {v} tidak valid')
        return v
    
    @validator('contact_preference')
    def validate_contact_preference(cls, v):
        valid_preferences = ['email', 'phone', 'whatsapp', 'video_call']
        if v not in valid_preferences:
            raise ValueError(f'Preferensi kontak {v} tidak valid')
        return v
    
    @validator('attachments')
    def validate_attachments(cls, v):
        if len(v) > 5:
            raise ValueError('Maksimal 5 lampiran per konsultasi')
        return v

class ConsultationUpdateDTO(BaseModel):
    """DTO untuk update konsultasi"""
    subject: Optional[str] = Field(None, min_length=5, max_length=200, description="Subjek konsultasi")
    message: Optional[str] = Field(None, min_length=10, max_length=2000, description="Pesan konsultasi")
    category: Optional[str] = Field(None, description="Kategori konsultasi")
    priority: Optional[str] = Field(None, description="Prioritas konsultasi")
    status: Optional[str] = Field(None, description="Status konsultasi")
    assigned_to: Optional[str] = Field(None, description="Ditugaskan kepada")
    contact_preference: Optional[str] = Field(None, description="Preferensi kontak")
    preferred_time: Optional[str] = Field(None, description="Waktu yang diinginkan")
    student_info: Optional[Dict[str, Any]] = Field(None, description="Informasi siswa")
    attachments: Optional[List[str]] = Field(None, description="URL lampiran")
    admin_notes: Optional[str] = Field(None, description="Catatan admin")
    
    @validator('category')
    def validate_category(cls, v):
        if v:
            valid_categories = [
                'pendaftaran', 'biaya', 'program', 'fasilitas', 'kurikulum',
                'kehidupan_santri', 'alumni', 'beasiswa', 'umum', 'lainnya'
            ]
            if v not in valid_categories:
                raise ValueError(f'Kategori {v} tidak valid')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        if v:
            valid_priorities = ['low', 'normal', 'high', 'urgent']
            if v not in valid_priorities:
                raise ValueError(f'Prioritas {v} tidak valid')
        return v
    
    @validator('status')
    def validate_status(cls, v):
        if v:
            valid_statuses = ['open', 'in_progress', 'waiting_response', 'resolved', 'closed']
            if v not in valid_statuses:
                raise ValueError(f'Status {v} tidak valid')
        return v

class ConsultationResponseCreateDTO(BaseModel):
    """DTO untuk membuat respons konsultasi"""
    message: str = Field(..., min_length=10, max_length=2000, description="Pesan respons")
    attachments: List[str] = Field(default=[], description="URL lampiran")
    is_internal: bool = Field(False, description="Catatan internal")
    
    @validator('attachments')
    def validate_attachments(cls, v):
        if len(v) > 3:
            raise ValueError('Maksimal 3 lampiran per respons')
        return v

class ConsultationResponseDTO(BaseModel):
    """DTO untuk respons konsultasi"""
    id: str = Field(description="ID respons")
    consultation_id: str = Field(description="ID konsultasi")
    user_id: str = Field(description="ID pengguna")
    user_name: str = Field(description="Nama pengguna")
    user_role: str = Field(description="Role pengguna")
    user_avatar: Optional[str] = Field(description="Avatar pengguna")
    message: str = Field(description="Pesan respons")
    attachments: List[str] = Field(description="URL lampiran")
    is_internal: bool = Field(description="Catatan internal")
    created_at: datetime = Field(description="Tanggal dibuat")
    updated_at: datetime = Field(description="Tanggal update")

class ConsultationResponseFullDTO(BaseResponseDTO):
    """DTO untuk response konsultasi lengkap"""
    ticket_number: str = Field(description="Nomor tiket")
    pesantren_id: str = Field(description="ID pesantren")
    pesantren_name: str = Field(description="Nama pesantren")
    user_id: str = Field(description="ID pengguna")
    user_name: str = Field(description="Nama pengguna")
    user_email: str = Field(description="Email pengguna")
    user_phone: str = Field(description="Telepon pengguna")
    subject: str = Field(description="Subjek konsultasi")
    message: str = Field(description="Pesan konsultasi")
    category: str = Field(description="Kategori konsultasi")
    priority: str = Field(description="Prioritas konsultasi")
    status: str = Field(description="Status konsultasi")
    assigned_to: Optional[str] = Field(description="Ditugaskan kepada")
    assigned_to_name: Optional[str] = Field(description="Nama yang ditugaskan")
    contact_preference: str = Field(description="Preferensi kontak")
    preferred_time: Optional[str] = Field(description="Waktu yang diinginkan")
    student_info: Optional[Dict[str, Any]] = Field(description="Informasi siswa")
    attachments: List[str] = Field(description="URL lampiran")
    responses: List[ConsultationResponseDTO] = Field(description="Daftar respons")
    response_count: int = Field(description="Jumlah respons")
    last_response_at: Optional[datetime] = Field(description="Respons terakhir")
    last_response_by: Optional[str] = Field(description="Respons terakhir oleh")
    resolution_time: Optional[int] = Field(description="Waktu penyelesaian (menit)")
    satisfaction_rating: Optional[int] = Field(description="Rating kepuasan")
    satisfaction_feedback: Optional[str] = Field(description="Feedback kepuasan")
    admin_notes: Optional[str] = Field(description="Catatan admin")
    due_date: Optional[datetime] = Field(description="Batas waktu")
    is_overdue: bool = Field(description="Lewat batas waktu")
    
class ConsultationSummaryDTO(BaseModel):
    """DTO untuk summary konsultasi (untuk list)"""
    id: str = Field(description="ID konsultasi")
    ticket_number: str = Field(description="Nomor tiket")
    pesantren_name: str = Field(description="Nama pesantren")
    user_name: str = Field(description="Nama pengguna")
    subject: str = Field(description="Subjek konsultasi")
    category: str = Field(description="Kategori konsultasi")
    priority: str = Field(description="Prioritas konsultasi")
    status: str = Field(description="Status konsultasi")
    assigned_to_name: Optional[str] = Field(description="Nama yang ditugaskan")
    response_count: int = Field(description="Jumlah respons")
    last_response_at: Optional[datetime] = Field(description="Respons terakhir")
    satisfaction_rating: Optional[int] = Field(description="Rating kepuasan")
    is_overdue: bool = Field(description="Lewat batas waktu")
    created_at: datetime = Field(description="Tanggal dibuat")
    updated_at: datetime = Field(description="Tanggal update")

class ConsultationSearchDTO(SearchDTO):
    """DTO untuk pencarian konsultasi"""
    pesantren_id: Optional[str] = Field(None, description="Filter pesantren")
    user_id: Optional[str] = Field(None, description="Filter pengguna")
    category: Optional[str] = Field(None, description="Filter kategori")
    priority: Optional[str] = Field(None, description="Filter prioritas")
    status: Optional[str] = Field(None, description="Filter status")
    assigned_to: Optional[str] = Field(None, description="Filter yang ditugaskan")
    is_overdue: Optional[bool] = Field(None, description="Filter lewat batas waktu")
    
class ConsultationFilterDTO(FilterDTO):
    """DTO untuk filter konsultasi"""
    pesantren_id: Optional[str] = Field(None, description="Filter pesantren")
    user_id: Optional[str] = Field(None, description="Filter pengguna")
    category: Optional[str] = Field(None, description="Filter kategori")
    priority: Optional[str] = Field(None, description="Filter prioritas")
    status: Optional[str] = Field(None, description="Filter status")
    assigned_to: Optional[str] = Field(None, description="Filter yang ditugaskan")
    contact_preference: Optional[str] = Field(None, description="Filter preferensi kontak")
    has_attachments: Optional[bool] = Field(None, description="Filter ada lampiran")
    has_student_info: Optional[bool] = Field(None, description="Filter ada info siswa")
    is_overdue: Optional[bool] = Field(None, description="Filter lewat batas waktu")
    satisfaction_rating: Optional[int] = Field(None, ge=1, le=5, description="Filter rating kepuasan")
    resolution_time_from: Optional[int] = Field(None, ge=0, description="Waktu penyelesaian dari (menit)")
    resolution_time_to: Optional[int] = Field(None, ge=0, description="Waktu penyelesaian sampai (menit)")
    due_date_from: Optional[datetime] = Field(None, description="Batas waktu dari")
    due_date_to: Optional[datetime] = Field(None, description="Batas waktu sampai")

class ConsultationStatsDTO(BaseModel):
    """DTO untuk statistik konsultasi"""
    total_consultations: int = Field(description="Total konsultasi")
    open_consultations: int = Field(description="Konsultasi terbuka")
    in_progress_consultations: int = Field(description="Konsultasi dalam proses")
    resolved_consultations: int = Field(description="Konsultasi selesai")
    overdue_consultations: int = Field(description="Konsultasi lewat batas waktu")
    consultations_today: int = Field(description="Konsultasi hari ini")
    consultations_this_week: int = Field(description="Konsultasi minggu ini")
    consultations_this_month: int = Field(description="Konsultasi bulan ini")
    average_resolution_time: float = Field(description="Rata-rata waktu penyelesaian (menit)")
    average_satisfaction_rating: float = Field(description="Rata-rata rating kepuasan")
    by_category: Dict[str, int] = Field(description="Statistik per kategori")
    by_priority: Dict[str, int] = Field(description="Statistik per prioritas")
    by_status: Dict[str, int] = Field(description="Statistik per status")
    by_pesantren: Dict[str, int] = Field(description="Statistik per pesantren")
    by_assigned_to: Dict[str, int] = Field(description="Statistik per yang ditugaskan")
    response_time_stats: Dict[str, float] = Field(description="Statistik waktu respons")
    satisfaction_distribution: Dict[str, int] = Field(description="Distribusi kepuasan")
    
class ConsultationAssignDTO(BaseModel):
    """DTO untuk menugaskan konsultasi"""
    assigned_to: str = Field(..., description="ID yang ditugaskan")
    notes: Optional[str] = Field(None, description="Catatan penugasan")
    due_date: Optional[datetime] = Field(None, description="Batas waktu")
    
    @validator('due_date')
    def validate_due_date(cls, v):
        if v and v <= datetime.now():
            raise ValueError('Batas waktu harus di masa depan')
        return v

class ConsultationStatusUpdateDTO(BaseModel):
    """DTO untuk update status konsultasi"""
    status: str = Field(..., description="Status baru")
    notes: Optional[str] = Field(None, description="Catatan")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['open', 'in_progress', 'waiting_response', 'resolved', 'closed']
        if v not in valid_statuses:
            raise ValueError(f'Status {v} tidak valid')
        return v

class ConsultationSatisfactionDTO(BaseModel):
    """DTO untuk rating kepuasan konsultasi"""
    rating: int = Field(..., ge=1, le=5, description="Rating kepuasan (1-5)")
    feedback: Optional[str] = Field(None, max_length=1000, description="Feedback kepuasan")
    
class ConsultationAnalyticsDTO(BaseModel):
    """DTO untuk analytics konsultasi"""
    pesantren_id: Optional[str] = Field(None, description="ID pesantren")
    total_consultations: int = Field(description="Total konsultasi")
    resolution_rate: float = Field(description="Tingkat penyelesaian (%)")
    average_resolution_time: float = Field(description="Rata-rata waktu penyelesaian (jam)")
    average_satisfaction_rating: float = Field(description="Rata-rata rating kepuasan")
    consultation_trend: List[Dict[str, Any]] = Field(description="Trend konsultasi")
    category_performance: Dict[str, Dict[str, Any]] = Field(description="Performa per kategori")
    agent_performance: Dict[str, Dict[str, Any]] = Field(description="Performa per agen")
    response_time_analysis: Dict[str, float] = Field(description="Analisis waktu respons")
    satisfaction_trend: List[Dict[str, Any]] = Field(description="Trend kepuasan")
    peak_hours: List[Dict[str, Any]] = Field(description="Jam sibuk")
    
class ConsultationBulkActionDTO(BaseModel):
    """DTO untuk aksi bulk pada konsultasi"""
    consultation_ids: List[str] = Field(..., min_items=1, description="ID konsultasi")
    action: str = Field(..., description="Aksi yang dilakukan")
    value: Optional[Any] = Field(None, description="Nilai untuk aksi")
    notes: Optional[str] = Field(None, description="Catatan")
    
    @validator('action')
    def validate_action(cls, v):
        valid_actions = ['assign', 'change_status', 'change_priority', 'close', 'delete']
        if v not in valid_actions:
            raise ValueError(f'Aksi {v} tidak valid')
        return v
    
    @validator('consultation_ids')
    def validate_consultation_ids(cls, v):
        if len(v) > 50:
            raise ValueError('Maksimal 50 konsultasi per aksi bulk')
        return v