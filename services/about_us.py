import logging
from typing import Dict, Any
from .base_service import BaseService
from models.about_us import AboutUsModel
from dto.about_us_dto import AboutUsResponseDTO, AboutUsUpdateDTO
from dto.base_dto import SuccessResponseDTO
from core.exceptions import ServiceException

class AboutUsService(BaseService[None, AboutUsModel]):
    def __init__(self):
        super().__init__(AboutUsModel)

    def get_resource_name(self) -> str:
        return "About Us"
    
    def get_about_us(self) -> SuccessResponseDTO:
        """Mengambil data 'About Us'."""
        try:
            about_us_data = self.model.get_about_us()
            if not about_us_data:
                # Jika belum ada data, kembalikan default kosong
                default_data = AboutUsResponseDTO(
                    description="Deskripsi belum diatur.",
                    why_us="Alasan memilih kami belum diatur.",
                    image_url=None # Ubah dari images=[] menjadi image_url=None
                )
                return self.create_success_response(data=default_data.dict(), message="Data 'About Us' belum diatur.")
            
            response_dto = AboutUsResponseDTO(**about_us_data)
            return self.create_success_response(data=response_dto.dict(), message="Data 'About Us' berhasil diambil.")

        except Exception as e:
            logging.error(f"Error getting About Us data: {e}", exc_info=True)
            raise ServiceException(message="Gagal mengambil data 'About Us'.")

    def update_about_us(self, data: Dict[str, Any], user_id: str) -> SuccessResponseDTO:
        """Memperbarui data 'About Us'."""
        try:
            update_dto = AboutUsUpdateDTO(**data)
            
            updated_data = self.model.update_about_us(update_dto.dict())
            if not updated_data:
                raise ServiceException("Gagal memperbarui data 'About Us' di database.")

            self.log_activity(user_id, "update", "about_us", updated_data.get("id"))
            
            response_dto = AboutUsResponseDTO(**updated_data)
            return self.create_success_response(data=response_dto.dict(), message="Data 'About Us' berhasil diperbarui.")

        except Exception as e:
            logging.error(f"Error updating About Us data: {e}", exc_info=True)
            raise ServiceException(message="Gagal memperbarui data 'About Us'.")