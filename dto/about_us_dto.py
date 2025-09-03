from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class AboutUsBaseDTO(BaseModel):
    """Base DTO for About Us content."""
    description: str = Field(..., min_length=20, description="Deskripsi lengkap tentang kami.")
    why_us: str = Field(..., min_length=20, description="Penjelasan mengapa memilih kami.")
    image_url: Optional[str] = Field(None, description="URL gambar utama untuk halaman 'About Us'.")

class AboutUsUpdateDTO(AboutUsBaseDTO):
    """DTO for creating or updating the About Us page."""
    pass

class AboutUsResponseDTO(AboutUsBaseDTO):
    """DTO for the response of the About Us page."""
    updated_at: Optional[datetime] = Field(None, description="Waktu terakhir diupdate.")
    
    class Config:
        from_attributes = True # Dulu 'orm_mode'