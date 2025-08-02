from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from .base_dto import BaseResponseDTO, SearchDTO, FilterDTO

class StudentDataDTO(BaseModel):
    """DTO untuk data siswa"""
    name: str = Field(..., min_length=2, max_length=100, description="Nama lengkap siswa")
    birth_date: date = Field(..., description="Tanggal lahir")
    birth_place: str = Field(..., min_length=2, max_length=100, description="Tempat lahir")
    gender: str = Field(..., description="Jenis kelamin")
    address: str = Field(..., min_length=10, description="Alamat lengkap")
    previous_school: Optional[str] = Field(None, description="Sekolah sebelumnya")
    previous_education_level: Optional[str] = Field(None, description="Jenjang pendidikan sebelumnya")
    graduation_year: Optional[int] = Field(None, description="Tahun lulus")
    achievements: Optional[List[str]] = Field(None, description="Prestasi")
    health_conditions: Optional[List[str]] = Field(None, description="Kondisi kesehatan")
    special_needs: Optional[List[str]] = Field(None, description="Kebutuhan khusus")
    
    @validator('gender')
    def validate_gender(cls, v):
        if v not in ['male', 'female']:
            raise ValueError('Gender harus male atau female')
        return v
    
    @validator('birth_date')
    def validate_birth_date(cls, v):
        today = date.today()
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        if age < 5 or age > 25:
            raise ValueError('Umur siswa harus antara 5-25 tahun')
        return v

class ParentDataDTO(BaseModel):
    """DTO untuk data orang tua"""
    father_name: str = Field(..., min_length=2, max_length=100, description="Nama ayah")
    father_occupation: Optional[str] = Field(None, description="Pekerjaan ayah")
    father_phone: Optional[str] = Field(None, description="Telepon ayah")
    mother_name: str = Field(..., min_length=2, max_length=100, description="Nama ibu")
    mother_occupation: Optional[str] = Field(None, description="Pekerjaan ibu")
    mother_phone: Optional[str] = Field(None, description="Telepon ibu")
    guardian_name: Optional[str] = Field(None, description="Nama wali")
    guardian_relation: Optional[str] = Field(None, description="Hubungan dengan wali")
    guardian_phone: Optional[str] = Field(None, description="Telepon wali")
    family_income: Optional[str] = Field(None, description="Penghasilan keluarga")
    family_address: str = Field(..., min_length=10, description="Alamat keluarga")

class ApplicationCreateDTO(BaseModel):
    """DTO untuk membuat aplikasi pendaftaran baru"""
    pesantren_id: str = Field(..., description="ID pesantren")
    program: str = Field(..., description="Program yang dipilih")
    education_level: str = Field(..., description="Jenjang pendidikan")
    student_data: StudentDataDTO = Field(..., description="Data siswa")
    parent_data: ParentDataDTO = Field(..., description="Data orang tua")
    motivation: str = Field(..., min_length=50, max_length=1000, description="Motivasi mendaftar")
    expectations: Optional[str] = Field(None, description="Harapan dari pesantren")
    preferred_start_date: Optional[date] = Field(None, description="Tanggal mulai yang diinginkan")
    emergency_contact: Dict[str, str] = Field(..., description="Kontak darurat")
    
    @validator('preferred_start_date')
    def validate_start_date(cls, v):
        if v and v <= date.today():
            raise ValueError('Tanggal mulai harus di masa depan')
        return v

class ApplicationUpdateDTO(BaseModel):
    """DTO untuk update aplikasi pendaftaran"""
    program: Optional[str] = Field(None, description="Program yang dipilih")
    education_level: Optional[str] = Field(None, description="Jenjang pendidikan")
    student_data: Optional[StudentDataDTO] = Field(None, description="Data siswa")
    parent_data: Optional[ParentDataDTO] = Field(None, description="Data orang tua")
    motivation: Optional[str] = Field(None, min_length=50, max_length=1000, description="Motivasi mendaftar")
    expectations: Optional[str] = Field(None, description="Harapan dari pesantren")
    preferred_start_date: Optional[date] = Field(None, description="Tanggal mulai yang diinginkan")
    emergency_contact: Optional[Dict[str, str]] = Field(None, description="Kontak darurat")
    status: Optional[str] = Field(None, description="Status aplikasi")
    admin_notes: Optional[str] = Field(None, description="Catatan admin")
    
    @validator('status')
    def validate_status(cls, v):
        if v:
            valid_statuses = [
                'draft', 'submitted', 'under_review', 'interview_scheduled',
                'interview_completed', 'accepted', 'rejected', 'waitlisted', 'cancelled'
            ]
            if v not in valid_statuses:
                raise ValueError(f'Status {v} tidak valid')
        return v

class ApplicationResponseDTO(BaseResponseDTO):
    """DTO untuk response aplikasi pendaftaran"""
    application_number: str = Field(description="Nomor pendaftaran")
    pesantren_id: str = Field(description="ID pesantren")
    pesantren_name: str = Field(description="Nama pesantren")
    parent_id: str = Field(description="ID orang tua")
    parent_name: str = Field(description="Nama orang tua")
    program: str = Field(description="Program yang dipilih")
    education_level: str = Field(description="Jenjang pendidikan")
    academic_year: str = Field(description="Tahun akademik")
    student_data: StudentDataDTO = Field(description="Data siswa")
    parent_data: ParentDataDTO = Field(description="Data orang tua")
    motivation: str = Field(description="Motivasi mendaftar")
    expectations: Optional[str] = Field(description="Harapan dari pesantren")
    preferred_start_date: Optional[date] = Field(description="Tanggal mulai yang diinginkan")
    emergency_contact: Dict[str, str] = Field(description="Kontak darurat")
    status: str = Field(description="Status aplikasi")
    status_history: List[Dict[str, Any]] = Field(description="Riwayat status")
    interview_date: Optional[datetime] = Field(description="Tanggal wawancara")
    interview_notes: Optional[str] = Field(description="Catatan wawancara")
    interview_result: Optional[str] = Field(description="Hasil wawancara")
    payment_status: str = Field(description="Status pembayaran")
    payment_amount: Optional[float] = Field(description="Jumlah pembayaran")
    payment_due_date: Optional[date] = Field(description="Batas waktu pembayaran")
    documents: List[Dict[str, str]] = Field(description="Dokumen yang diupload")
    admin_notes: Optional[str] = Field(description="Catatan admin")
    rejection_reason: Optional[str] = Field(description="Alasan penolakan")
    
class ApplicationSummaryDTO(BaseModel):
    """DTO untuk summary aplikasi (untuk list)"""
    id: str = Field(description="ID aplikasi")
    application_number: str = Field(description="Nomor pendaftaran")
    pesantren_name: str = Field(description="Nama pesantren")
    student_name: str = Field(description="Nama siswa")
    program: str = Field(description="Program")
    education_level: str = Field(description="Jenjang pendidikan")
    status: str = Field(description="Status aplikasi")
    payment_status: str = Field(description="Status pembayaran")
    interview_date: Optional[datetime] = Field(description="Tanggal wawancara")
    created_at: datetime = Field(description="Tanggal pendaftaran")
    updated_at: datetime = Field(description="Update terakhir")

class ApplicationSearchDTO(SearchDTO):
    """DTO untuk pencarian aplikasi"""
    pesantren_id: Optional[str] = Field(None, description="Filter pesantren")
    parent_id: Optional[str] = Field(None, description="Filter orang tua")
    status: Optional[str] = Field(None, description="Filter status")
    program: Optional[str] = Field(None, description="Filter program")
    education_level: Optional[str] = Field(None, description="Filter jenjang pendidikan")
    academic_year: Optional[str] = Field(None, description="Filter tahun akademik")
    payment_status: Optional[str] = Field(None, description="Filter status pembayaran")
    
class ApplicationFilterDTO(FilterDTO):
    """DTO untuk filter aplikasi"""
    pesantren_id: Optional[str] = Field(None, description="Filter pesantren")
    parent_id: Optional[str] = Field(None, description="Filter orang tua")
    status: Optional[str] = Field(None, description="Filter status")
    program: Optional[str] = Field(None, description="Filter program")
    education_level: Optional[str] = Field(None, description="Filter jenjang pendidikan")
    academic_year: Optional[str] = Field(None, description="Filter tahun akademik")
    payment_status: Optional[str] = Field(None, description="Filter status pembayaran")
    interview_scheduled: Optional[bool] = Field(None, description="Filter wawancara terjadwal")
    interview_completed: Optional[bool] = Field(None, description="Filter wawancara selesai")
    has_documents: Optional[bool] = Field(None, description="Filter ada dokumen")
    student_gender: Optional[str] = Field(None, description="Filter gender siswa")
    student_age_from: Optional[int] = Field(None, description="Filter umur siswa dari")
    student_age_to: Optional[int] = Field(None, description="Filter umur siswa sampai")
    preferred_start_date_from: Optional[date] = Field(None, description="Filter tanggal mulai dari")
    preferred_start_date_to: Optional[date] = Field(None, description="Filter tanggal mulai sampai")

class ApplicationStatsDTO(BaseModel):
    """DTO untuk statistik aplikasi"""
    total_applications: int = Field(description="Total aplikasi")
    pending_applications: int = Field(description="Aplikasi pending")
    accepted_applications: int = Field(description="Aplikasi diterima")
    rejected_applications: int = Field(description="Aplikasi ditolak")
    interview_scheduled: int = Field(description="Wawancara terjadwal")
    payment_completed: int = Field(description="Pembayaran selesai")
    applications_today: int = Field(description="Aplikasi hari ini")
    applications_this_week: int = Field(description="Aplikasi minggu ini")
    applications_this_month: int = Field(description="Aplikasi bulan ini")
    by_status: Dict[str, int] = Field(description="Statistik per status")
    by_program: Dict[str, int] = Field(description="Statistik per program")
    by_education_level: Dict[str, int] = Field(description="Statistik per jenjang")
    by_pesantren: Dict[str, int] = Field(description="Statistik per pesantren")
    conversion_rate: float = Field(description="Tingkat konversi (%)")
    
class ApplicationStatusUpdateDTO(BaseModel):
    """DTO untuk update status aplikasi"""
    status: str = Field(..., description="Status baru")
    notes: Optional[str] = Field(None, description="Catatan")
    reason: Optional[str] = Field(None, description="Alasan perubahan status")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = [
            'draft', 'submitted', 'under_review', 'interview_scheduled',
            'interview_completed', 'accepted', 'rejected', 'waitlisted', 'cancelled'
        ]
        if v not in valid_statuses:
            raise ValueError(f'Status {v} tidak valid')
        return v

class ApplicationInterviewDTO(BaseModel):
    """DTO untuk jadwal wawancara"""
    interview_date: datetime = Field(..., description="Tanggal dan waktu wawancara")
    interview_type: str = Field(..., description="Tipe wawancara")
    interview_location: Optional[str] = Field(None, description="Lokasi wawancara")
    interview_notes: Optional[str] = Field(None, description="Catatan wawancara")
    interviewer: Optional[str] = Field(None, description="Pewawancara")
    
    @validator('interview_type')
    def validate_interview_type(cls, v):
        valid_types = ['online', 'offline', 'phone', 'video_call']
        if v not in valid_types:
            raise ValueError(f'Tipe wawancara {v} tidak valid')
        return v
    
    @validator('interview_date')
    def validate_interview_date(cls, v):
        if v <= datetime.now():
            raise ValueError('Tanggal wawancara harus di masa depan')
        return v

class ApplicationPaymentDTO(BaseModel):
    """DTO untuk pembayaran aplikasi"""
    payment_status: str = Field(..., description="Status pembayaran")
    payment_amount: float = Field(..., gt=0, description="Jumlah pembayaran")
    payment_method: Optional[str] = Field(None, description="Metode pembayaran")
    payment_reference: Optional[str] = Field(None, description="Referensi pembayaran")
    payment_date: Optional[datetime] = Field(None, description="Tanggal pembayaran")
    payment_due_date: Optional[date] = Field(None, description="Batas waktu pembayaran")
    payment_notes: Optional[str] = Field(None, description="Catatan pembayaran")
    
    @validator('payment_status')
    def validate_payment_status(cls, v):
        valid_statuses = ['pending', 'paid', 'failed', 'refunded', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status pembayaran {v} tidak valid')
        return v

class ApplicationDocumentDTO(BaseModel):
    """DTO untuk dokumen aplikasi"""
    document_type: str = Field(..., description="Tipe dokumen")
    document_name: str = Field(..., description="Nama dokumen")
    document_url: str = Field(..., description="URL dokumen")
    document_size: Optional[int] = Field(None, description="Ukuran dokumen (bytes)")
    is_required: bool = Field(True, description="Dokumen wajib")
    is_verified: bool = Field(False, description="Dokumen terverifikasi")
    verification_notes: Optional[str] = Field(None, description="Catatan verifikasi")
    
    @validator('document_type')
    def validate_document_type(cls, v):
        valid_types = [
            'birth_certificate', 'family_card', 'student_photo', 'parent_id',
            'school_certificate', 'health_certificate', 'recommendation_letter',
            'achievement_certificate', 'other'
        ]
        if v not in valid_types:
            raise ValueError(f'Tipe dokumen {v} tidak valid')
        return v