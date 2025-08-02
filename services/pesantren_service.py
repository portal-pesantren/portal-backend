from typing import Dict, List, Optional, Any
from datetime import datetime
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
from .base_service import BaseService, NotFoundException, DuplicateException, ValidationException

class PesantrenService(BaseService[PesantrenCreateDTO, PesantrenModel]):
    """Service untuk mengelola pesantren"""
    
    def __init__(self):
        super().__init__(PesantrenModel)
    
    def get_resource_name(self) -> str:
        return "Pesantren"
    
    def create_pesantren(self, data: Dict[str, Any], user_id: str) -> SuccessResponseDTO:
        """Membuat pesantren baru"""
        try:
            # Validasi input menggunakan DTO
            create_dto = self.validate_dto(PesantrenCreateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(create_dto.dict())
            
            # Check duplicate name
            existing = self.model.find_one({"name": sanitized_data["name"]})
            if existing:
                raise DuplicateException("Pesantren", "nama", sanitized_data["name"])
            
            # Add metadata
            sanitized_data.update({
                "created_by": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "is_active": True,
                "is_featured": False,
                "student_count": 0,
                "rating_average": 0.0,
                "rating_count": 0,
                "view_count": 0
            })
            
            # Create pesantren
            pesantren = self.model.create(sanitized_data)
            
            # Log activity
            self.log_activity(user_id, "create", "pesantren", pesantren["_id"])
            
            # Convert to response DTO
            response_data = PesantrenResponseDTO(**pesantren)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Pesantren berhasil dibuat"
            )
            
        except ValidationException as e:
            return self.create_validation_error_response(e.errors)
        except DuplicateException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal membuat pesantren",
                code="CREATE_ERROR"
            )
    
    def get_pesantren_by_id(self, pesantren_id: str) -> SuccessResponseDTO:
        """Mendapatkan pesantren berdasarkan ID"""
        try:
            pesantren = self.model.find_by_id(pesantren_id)
            if not pesantren:
                raise NotFoundException("Pesantren", pesantren_id)
            
            # Increment view count
            self.model.update_by_id(pesantren_id, {"$inc": {"view_count": 1}})
            pesantren["view_count"] = pesantren.get("view_count", 0) + 1
            
            response_data = PesantrenResponseDTO(**pesantren)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Pesantren berhasil ditemukan"
            )
            
        except NotFoundException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil data pesantren",
                code="GET_ERROR"
            )
    
    def get_pesantren_list(
        self, 
        search_params: Optional[Dict[str, Any]] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan daftar pesantren dengan pencarian dan filter"""
        try:
            # Validate DTOs
            search_dto = None
            if search_params:
                search_dto = self.validate_dto(PesantrenSearchDTO, search_params)
            
            filter_dto = None
            if filter_params:
                filter_dto = self.validate_dto(PesantrenFilterDTO, filter_params)
            
            pagination_dto = PaginationDTO(**(pagination or {}))
            
            # Build query
            query = {"is_active": True}
            
            # Apply search
            if search_dto and search_dto.query:
                query["$text"] = {"$search": search_dto.query}
            
            # Apply filters
            if filter_dto:
                if filter_dto.location:
                    query["location.province"] = filter_dto.location
                if filter_dto.programs:
                    query["programs"] = {"$in": filter_dto.programs}
                if filter_dto.min_rating:
                    query["rating_average"] = {"$gte": filter_dto.min_rating}
                if filter_dto.max_cost:
                    query["cost.monthly"] = {"$lte": filter_dto.max_cost}
                if filter_dto.facilities:
                    query["facilities"] = {"$all": filter_dto.facilities}
                if filter_dto.is_featured is not None:
                    query["is_featured"] = filter_dto.is_featured
            
            # Get data with pagination
            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            pesantren_list = self.model.find_many(
                query=query,
                skip=skip,
                limit=pagination_dto.limit,
                sort=[("is_featured", -1), ("rating_average", -1), ("created_at", -1)]
            )
            
            total = self.model.count_documents(query)
            
            # Convert to summary DTOs
            response_data = [
                PesantrenSummaryDTO(**pesantren).dict() 
                for pesantren in pesantren_list
            ]
            
            return self.create_paginated_response(
                data=response_data,
                pagination=pagination_dto,
                total=total,
                message="Daftar pesantren berhasil diambil"
            )
            
        except ValidationException as e:
            return self.create_validation_error_response(e.errors)
        except Exception as e:
            return self.create_error_response(
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
            # Check if pesantren exists
            self.check_exists(pesantren_id, "Pesantren")
            
            # Validate input
            update_dto = self.validate_dto(PesantrenUpdateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(update_dto.dict(exclude_unset=True))
            
            # Check duplicate name if name is being updated
            if "name" in sanitized_data:
                existing = self.model.find_one({
                    "name": sanitized_data["name"],
                    "_id": {"$ne": pesantren_id}
                })
                if existing:
                    raise DuplicateException("Pesantren", "nama", sanitized_data["name"])
            
            # Add update metadata
            sanitized_data.update({
                "updated_by": user_id,
                "updated_at": datetime.now()
            })
            
            # Update pesantren
            updated_pesantren = self.model.update_by_id(pesantren_id, sanitized_data)
            
            # Log activity
            self.log_activity(user_id, "update", "pesantren", pesantren_id, sanitized_data)
            
            response_data = PesantrenResponseDTO(**updated_pesantren)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Pesantren berhasil diperbarui"
            )
            
        except (ValidationException, NotFoundException, DuplicateException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memperbarui pesantren",
                code="UPDATE_ERROR"
            )
    
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
            
            response_data = [
                PesantrenSummaryDTO(**pesantren).dict() 
                for pesantren in pesantren_list
            ]
            
            return self.create_success_response(
                data=response_data,
                message="Pesantren unggulan berhasil diambil"
            )
            
        except Exception as e:
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
            # Check if pesantren exists
            self.check_exists(pesantren_id, "Pesantren")
            
            # Update featured status
            self.model.set_featured_status(pesantren_id, is_featured)
            
            # Log activity
            action = "set_featured" if is_featured else "unset_featured"
            self.log_activity(user_id, action, "pesantren", pesantren_id)
            
            message = "Pesantren berhasil dijadikan unggulan" if is_featured else "Status unggulan pesantren berhasil dihapus"
            
            return self.create_success_response(
                data={"id": pesantren_id, "is_featured": is_featured},
                message=message
            )
            
        except NotFoundException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
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