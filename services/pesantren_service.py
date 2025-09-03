from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from bson import ObjectId
from models.pesantren import PesantrenModel
from dto.pesantren_dto import (
    PesantrenCreateDTO,
    PesantrenUpdateDTO,
    PesantrenResponseDTO,
    PesantrenSummaryDTO,
    PesantrenSearchDTO,
    PesantrenFilterDTO,
    PesantrenStatsDTO,
    PesantrenLocationStatsDTO,
    PesantrenProgramStatsDTO
)
from dto.base_dto import PaginationDTO, PaginatedResponseDTO, SuccessResponseDTO
from .base_service import BaseService
from pydantic import ValidationError
from core.exceptions import NotFoundException, DuplicateException, ValidationException, ServiceException

class PesantrenService(BaseService[PesantrenCreateDTO, PesantrenModel]):
    """Service untuk mengelola pesantren"""
    
    def __init__(self):
        super().__init__(PesantrenModel)
    
    def get_resource_name(self) -> str:
        return "Pesantren"
    
    def create_pesantren(self, data: Dict[str, Any], user_id: str) -> SuccessResponseDTO:
        """Membuat pesantren baru"""
        try:
            existing = self.model.find_one({"name": data.get("name")})
            if existing:
                raise DuplicateException("Pesantren", "nama", data.get("name"))

            sanitized_data = data.copy()
            sanitized_data.update({"created_by": user_id})

            pesantren_created = self.model.create_pesantren(sanitized_data)
            
            new_pesantren_id = pesantren_created.get("id")
            self.log_activity(user_id, "create", "pesantren", new_pesantren_id)
            
            # --- PERBAIKAN DI SINI ---
            # Ganti pemanggilan mapper dengan inisialisasi DTO langsung
            response_data_dto = PesantrenResponseDTO(**pesantren_created)
            
            return self.create_success_response(
                # Gunakan by_alias=True agar JSON output sesuai nama field DTO
                data=response_data_dto.dict(by_alias=True),
                message="Pesantren berhasil dibuat"
            )
        
        except (ValidationException, DuplicateException) as e:
            raise e
        except Exception as e:
            logging.error(f"Error creating pesantren: {str(e)}", exc_info=True)
            raise ServiceException(message="Gagal membuat pesantren", code="CREATE_ERROR")
    
    def get_pesantren_by_id(self, pesantren_id: str) -> SuccessResponseDTO:
        try:
            pesantren = self.model.find_by_id(pesantren_id)
            if not pesantren:
                raise NotFoundException("Pesantren", pesantren_id)
            
            # Increment view count
            self.model.increment_view(pesantren_id)
            pesantren["view_count"] = pesantren.get("view_count", 0) + 1
            
            # Langsung gunakan Pydantic DTO, tanpa mapper
            response_data = PesantrenResponseDTO(**pesantren)
            
            return self.create_success_response(
                data=response_data.dict(by_alias=True),
                message="Pesantren berhasil ditemukan"
            )
        except ValidationError as e:
            logging.error(f"Pydantic validation error for ID {pesantren_id}: {e}", exc_info=True)
            raise ServiceException(message=f"Data pesantren tidak valid: {e}", status_code=500)
        except NotFoundException as e:
            raise e
        except Exception as e:
            logging.error(f"Error getting pesantren by ID {pesantren_id}: {e}", exc_info=True)
            raise ServiceException(message="Gagal mengambil data pesantren")
    
    def get_pesantren_list(
        self, 
        search_params: Optional[Dict[str, Any]] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan daftar pesantren dengan pencarian dan filter"""
        try:
            search_dto = self.validate_dto(PesantrenSearchDTO, search_params or {})
            filter_dto = self.validate_dto(PesantrenFilterDTO, filter_params or {})
            pagination_dto = PaginationDTO(**(pagination or {}))
            
            query = {"is_active": True}
            
            if search_dto and search_dto.query:
                query["$text"] = {"$search": search_dto.query}
            
            if filter_dto:
                if filter_dto.province:
                    query["location.province"] = filter_dto.province
                if filter_dto.city:
                    query["location.city"] = filter_dto.city
                if filter_dto.is_featured is not None:
                    query["is_featured"] = filter_dto.is_featured

            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            pesantren_list = self.model.find_many(
                filter_dict=query,
                skip=skip,
                limit=pagination_dto.limit,
                sort=[("is_featured", -1), ("rating_average", -1), ("created_at", -1)]
            )
            
            total = self.model.count(query)
            
            if not pesantren_list:
                return self.create_paginated_response(
                    data=[], pagination=pagination_dto, total=0, message="Tidak ada pesantren yang ditemukan"
                )
            
            response_data = []
            for pesantren in pesantren_list:
                try:
                    location_data = pesantren.get('location', {})
                    location_summary = {
                        'city': location_data.get('city', ''),
                        'province': location_data.get('province', '')
                    }
                    
                    # LANGKAH 2: Gunakan .get() dengan nilai default saat membuat DTO
                    # Ini akan mencegah ValidationError jika field tidak ada di database
                    summary_dto = PesantrenSummaryDTO(**pesantren)
                    
                    response_data.append(summary_dto.dict())
                except ValidationError as dto_error:
                    logging.error(f"Error converting pesantren {pesantren.get('id')} to DTO: {dto_error}")
                    continue
            
            return self.create_paginated_response(
                data=response_data, pagination=pagination_dto, total=total, message="Daftar pesantren berhasil diambil"
            )
            
        except Exception as e:
            logging.error(f"Error in get_pesantren_list service: {e}", exc_info=True)
            raise ServiceException(
                message="Gagal mengambil daftar pesantren",
                code="LIST_ERROR"
            )
    
    def update_pesantren(
        self, 
        pesantren_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Update pesantren"""
        try:
            pesantren_to_update = self.model.find_by_id(pesantren_id)
            if not pesantren_to_update:
                raise NotFoundException("Pesantren", pesantren_id)
            
            update_dto = self.validate_dto(PesantrenUpdateDTO, data)
            
            sanitized_data = update_dto.dict(exclude_unset=True)
            sanitized_data.update({"updated_by": user_id})
            
            if "name" in sanitized_data and sanitized_data["name"] != pesantren_to_update.get("name"):
                existing = self.model.find_one({
                    "name": sanitized_data["name"],
                    "_id": {"$ne": ObjectId(pesantren_id)} # Gunakan ObjectId untuk query
                })
                if existing:
                    raise DuplicateException("Pesantren", "nama", sanitized_data["name"])
            
            updated_pesantren = self.model.find_one_and_update(
                {"_id": pesantren_id},
                sanitized_data
            )

            if not updated_pesantren:
                raise ServiceException(message="Gagal memperbarui pesantren", status_code=500)

            self.log_activity(user_id, "update", "pesantren", pesantren_id, sanitized_data)
            
            # --- PERBAIKAN DI SINI ---
            # Ganti pemanggilan mapper dengan inisialisasi DTO langsung
            response_data_dto = PesantrenResponseDTO(**updated_pesantren)
            
            return self.create_success_response(
                # Gunakan by_alias=True agar JSON output sesuai nama field DTO
                data=response_data_dto.dict(by_alias=True),
                message="Pesantren berhasil diperbarui"
            )
            
        except (ValidationException, NotFoundException, DuplicateException) as e:
            raise e
        except Exception as e:
            logging.error(f"Error updating pesantren: {str(e)}", exc_info=True)
            raise ServiceException(message="Gagal memperbarui pesantren", code="UPDATE_ERROR")

    
    def delete_pesantren(self, pesantren_id: str, user_id: str) -> SuccessResponseDTO:
        """Soft delete pesantren"""
        try:
            # Check if pesantren exists
            self.check_exists(pesantren_id, "Pesantren")
            
            # Soft delete
            self.model.update_by_id(pesantren_id, {
                "is_active": False,
                "deleted_by": user_id,
                "deleted_at": datetime.now()
            })
            
            # Log activity
            self.log_activity(user_id, "delete", "pesantren", pesantren_id)
            
            return self.create_success_response(
                data={"id": pesantren_id},
                message="Pesantren berhasil dihapus"
            )
            
        except NotFoundException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal menghapus pesantren",
                code="DELETE_ERROR"
            )
    
    def get_featured_pesantren(self, limit: int = 10) -> SuccessResponseDTO:
        """Mendapatkan pesantren unggulan"""
        try:
            pesantren_list = self.model.get_featured_pesantren(limit)
            
            response_data = []
            for pesantren in pesantren_list:
                try:
                    # Ambil data lokasi yang kompleks dari database
                    location_data = pesantren.get('location', {})
                    # Buat dictionary sederhana (summary) sesuai harapan DTO
                    location_summary = {
                        'city': location_data.get('city', ''),
                        'province': location_data.get('province', '')
                    }
                    
                    # Buat DTO secara manual, jangan menggunakan shortcut (**pesantren)
                    summary_dto = PesantrenSummaryDTO(
                        id=str(pesantren.get('_id', pesantren.get('id', ''))),
                        name=pesantren.get('name', ''),
                        slug=pesantren.get('slug', ''),
                        location=location_summary, # Gunakan summary yang sudah ditransformasi
                        monthly_fee=pesantren.get('monthly_fee', 0.0),
                        rating_average=pesantren.get('rating_average', 0.0),
                        rating_count=pesantren.get('rating_count', 0),
                        is_featured=pesantren.get('is_featured', False),
                        images=pesantren.get('images', []),
                        programs=pesantren.get('programs', []),
                        education_levels=pesantren.get('education_levels', [])
                    )
                    response_data.append(summary_dto.dict())
                except Exception as dto_error:
                    logging.error(f"Error converting featured pesantren to DTO: {dto_error}")
                    logging.error(f"Pesantren data causing error: {pesantren}")
                    continue # Lanjutkan ke data berikutnya jika satu data gagal

            return self.create_success_response(
                data=response_data,
                message="Pesantren unggulan berhasil diambil"
            )
            
        except Exception as e:
            logging.error(f"Failed to get featured pesantren: {e}", exc_info=True)
            return self.create_error_response(
                message="Gagal mengambil pesantren unggulan",
                code="FEATURED_ERROR"
            )

    
    def get_popular_pesantren(self, limit: int = 10) -> SuccessResponseDTO:
        """Mendapatkan pesantren populer"""
        try:
            pesantren_list = self.model.get_popular_pesantren(limit)
            
            response_data = [
                PesantrenSummaryDTO(**pesantren).dict() 
                for pesantren in pesantren_list
            ]
            
            return self.create_success_response(
                data=response_data,
                message="Pesantren populer berhasil diambil"
            )
            
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil pesantren populer",
                code="POPULAR_ERROR"
            )
    
    def set_featured_status(
        self,
        pesantren_id: str,
        is_featured: bool,
        user_id: str
    ) -> SuccessResponseDTO:
        """Set status unggulan pesantren"""
        try:
            # Cek apakah pesantren ada
            pesantren = self.model.find_by_id(pesantren_id)
            if not pesantren:
                raise NotFoundException("Pesantren", pesantren_id)

            # GANTI NAMA METODE DI BAWAH INI
            # DARI: self.model.set_featured_status(pesantren_id, is_featured)
            # MENJADI:
            update_result = self.model.set_featured(pesantren_id, is_featured)
            
            if not update_result:
                # Tambahkan penanganan jika update gagal di level model
                raise ServiceException(
                    message="Gagal mengubah status unggulan di database",
                    code="DATABASE_UPDATE_ERROR"
                )

            # Log aktivitas
            action = "set_featured" if is_featured else "unset_featured"
            self.log_activity(user_id, action, "pesantren", pesantren_id)

            message = "Pesantren berhasil dijadikan unggulan" if is_featured else "Status unggulan pesantren berhasil dihapus"

            return self.create_success_response(
                data={"id": pesantren_id, "is_featured": is_featured},
                message=message
            )

        except NotFoundException as e:
            # Biarkan router menangani ini dengan melempar exception
            raise e
        except Exception as e:
            # Ubah ini agar melempar ServiceException
            logging.error(f"Error setting featured status: {str(e)}", exc_info=True)
            raise ServiceException(
                message="Gagal mengubah status unggulan",
                code="FEATURED_STATUS_ERROR"
            )
    
    def get_pesantren_stats(self) -> SuccessResponseDTO:
        """Mendapatkan statistik pesantren"""
        try:
            stats = self.model.get_stats()
            response_data = PesantrenStatsDTO(**stats)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Statistik pesantren berhasil diambil"
            )
            
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil statistik pesantren",
                code="STATS_ERROR"
            )
    
    def get_location_stats(self) -> SuccessResponseDTO:
        """Mendapatkan statistik berdasarkan lokasi"""
        try:
            locations = self.model.get_available_locations()
            response_data = [PesantrenLocationStatsDTO(**loc) for loc in locations]
            
            return self.create_success_response(
                data=response_data,
                message="Statistik lokasi berhasil diambil"
            )
            
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil statistik lokasi",
                code="LOCATION_STATS_ERROR"
            )
    
    def get_program_stats(self) -> SuccessResponseDTO:
        """Mendapatkan statistik berdasarkan program"""
        try:
            programs = self.model.get_available_programs()
            response_data = [PesantrenProgramStatsDTO(**prog) for prog in programs]
            
            return self.create_success_response(
                data=response_data,
                message="Statistik program berhasil diambil"
            )
            
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil statistik program",
                code="PROGRAM_STATS_ERROR"
            )