from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from models.consultation import ConsultationModel
from models.user import UserModel
from dto.consultation_dto import (
    ConsultationCreateDTO,
    ConsultationUpdateDTO,
    ConsultationResponseCreateDTO,
    ConsultationResponseDTO,
    ConsultationResponseFullDTO,
    ConsultationSummaryDTO,
    ConsultationSearchDTO,
    ConsultationFilterDTO,
    ConsultationStatsDTO,
    ConsultationAssignDTO,
    ConsultationStatusUpdateDTO,
    ConsultationSatisfactionDTO,
    ConsultationAnalyticsDTO,
    ConsultationBulkActionDTO
)
from dto.base_dto import PaginationDTO, PaginatedResponseDTO, SuccessResponseDTO
from .base_service import BaseService, NotFoundException, DuplicateException, ValidationException, PermissionException

class ConsultationService(BaseService[ConsultationCreateDTO, ConsultationModel]):
    """Service untuk mengelola konsultasi pesantren"""
    
    def __init__(self):
        super().__init__(ConsultationModel)
        self.user_model = UserModel()
    
    def get_resource_name(self) -> str:
        return "Consultation"
    
    def create_consultation(self, data: Dict[str, Any], user_id: str) -> SuccessResponseDTO:
        """Membuat konsultasi baru"""
        try:
            # Validasi input
            consultation_dto = self.validate_dto(ConsultationCreateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(consultation_dto.dict())
            
            # Check if user exists
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            # Prepare consultation data
            consultation_data = {
                "user_id": user_id,
                "subject": sanitized_data["subject"],
                "message": sanitized_data["message"],
                "category": sanitized_data["category"],
                "priority": sanitized_data.get("priority", "medium"),
                "status": "open",
                "is_anonymous": sanitized_data.get("is_anonymous", False),
                "contact_email": sanitized_data.get("contact_email"),
                "contact_phone": sanitized_data.get("contact_phone"),
                "attachments": sanitized_data.get("attachments", []),
                "tags": sanitized_data.get("tags", []),
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Create consultation
            consultation = self.model.create_consultation(consultation_data)
            
            # Log activity
            self.log_activity(user_id, "create", "consultation", consultation["_id"], consultation_data)
            
            # Convert to response DTO
            response_data = ConsultationResponseDTO(**consultation)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Konsultasi berhasil dibuat"
            )
            
        except (ValidationException, NotFoundException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal membuat konsultasi",
                code="CREATE_CONSULTATION_ERROR"
            )
    
    def get_consultation_by_id(
        self, 
        consultation_id: str, 
        user_id: str = None,
        include_responses: bool = True
    ) -> SuccessResponseDTO:
        """Mendapatkan konsultasi berdasarkan ID"""
        try:
            consultation = self.model.get_consultation_with_details(consultation_id)
            if not consultation:
                raise NotFoundException("Consultation", consultation_id)
            
            # Check permission (user can only see their own consultation or admin/consultant can see all)
            if user_id:
                user = self.user_model.find_by_id(user_id)
                if (consultation["user_id"] != user_id and 
                    user.get("role") not in ["admin", "consultant"]):
                    raise PermissionException("view", "consultation")
            
            # Convert to appropriate response DTO
            if include_responses:
                response_data = ConsultationResponseFullDTO(**consultation)
            else:
                response_data = ConsultationResponseDTO(**consultation)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Konsultasi berhasil diambil"
            )
            
        except (NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil konsultasi",
                code="GET_CONSULTATION_ERROR"
            )
    
    def get_consultations_list(
        self,
        search_params: Optional[Dict[str, Any]] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None,
        user_id: str = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan daftar konsultasi"""
        try:
            # Check user role
            user_role = None
            if user_id:
                user = self.user_model.find_by_id(user_id)
                user_role = user.get("role") if user else None
            
            # Validate DTOs
            search_dto = None
            if search_params:
                search_dto = self.validate_dto(ConsultationSearchDTO, search_params)
            
            filter_dto = None
            if filter_params:
                filter_dto = self.validate_dto(ConsultationFilterDTO, filter_params)
            
            pagination_dto = PaginationDTO(**(pagination or {}))
            
            # Build query based on user role
            query = {}
            
            # Regular users can only see their own consultations
            if user_role not in ["admin", "consultant"]:
                query["user_id"] = user_id
            
            # Apply search
            if search_dto and search_dto.query:
                query["$or"] = [
                    {"subject": {"$regex": search_dto.query, "$options": "i"}},
                    {"message": {"$regex": search_dto.query, "$options": "i"}},
                    {"tags": {"$in": [search_dto.query]}}
                ]
            
            # Apply filters
            if filter_dto:
                if filter_dto.status:
                    query["status"] = filter_dto.status
                if filter_dto.category:
                    query["category"] = filter_dto.category
                if filter_dto.priority:
                    query["priority"] = filter_dto.priority
                if filter_dto.assigned_to:
                    query["assigned_to"] = filter_dto.assigned_to
                if filter_dto.user_id and user_role in ["admin", "consultant"]:
                    query["user_id"] = filter_dto.user_id
                if filter_dto.created_from:
                    query["created_at"] = {"$gte": filter_dto.created_from}
                if filter_dto.created_to:
                    query.setdefault("created_at", {})["$lte"] = filter_dto.created_to
            
            # Get data with pagination
            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            # Determine sort order
            sort_order = []
            if search_dto and search_dto.sort_by:
                if search_dto.sort_by == "date":
                    sort_order.append(("created_at", -1 if search_dto.sort_order == "desc" else 1))
                elif search_dto.sort_by == "priority":
                    # Custom priority order: high, medium, low
                    priority_order = {"high": 3, "medium": 2, "low": 1}
                    sort_order.append(("priority_order", -1 if search_dto.sort_order == "desc" else 1))
                elif search_dto.sort_by == "status":
                    sort_order.append(("status", 1 if search_dto.sort_order == "asc" else -1))
            else:
                sort_order.append(("created_at", -1))  # Default: newest first
            
            consultations = self.model.search_consultations(
                query=query,
                skip=skip,
                limit=pagination_dto.limit,
                sort=sort_order
            )
            
            total = self.model.count_documents(query)
            
            # Convert to response DTOs
            response_data = [ConsultationSummaryDTO(**consultation).dict() for consultation in consultations]
            
            return self.create_paginated_response(
                data=response_data,
                pagination=pagination_dto,
                total=total,
                message="Daftar konsultasi berhasil diambil"
            )
            
        except ValidationException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil daftar konsultasi",
                code="GET_CONSULTATIONS_ERROR"
            )
    
    def update_consultation(
        self, 
        consultation_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Update konsultasi"""
        try:
            # Check if consultation exists
            consultation = self.model.find_by_id(consultation_id)
            if not consultation:
                raise NotFoundException("Consultation", consultation_id)
            
            # Check permission (only owner can update)
            if consultation["user_id"] != user_id:
                raise PermissionException("update", "consultation")
            
            # Check if consultation can be updated (only open consultations)
            if consultation["status"] not in ["open", "in_progress"]:
                raise ValidationException("Konsultasi yang sudah selesai tidak dapat diubah")
            
            # Validasi input
            update_dto = self.validate_dto(ConsultationUpdateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(update_dto.dict(exclude_unset=True))
            
            # Add update metadata
            sanitized_data["updated_at"] = datetime.now()
            
            # Update consultation
            updated_consultation = self.model.update_consultation(consultation_id, sanitized_data)
            
            # Log activity
            self.log_activity(user_id, "update", "consultation", consultation_id, sanitized_data)
            
            response_data = ConsultationResponseDTO(**updated_consultation)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Konsultasi berhasil diperbarui"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memperbarui konsultasi",
                code="UPDATE_CONSULTATION_ERROR"
            )
    
    def create_response(
        self, 
        consultation_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Membuat respons untuk konsultasi"""
        try:
            # Check if consultation exists
            consultation = self.model.find_by_id(consultation_id)
            if not consultation:
                raise NotFoundException("Consultation", consultation_id)
            
            # Check permission
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            # Only consultant/admin or consultation owner can respond
            if (user.get("role") not in ["admin", "consultant"] and 
                consultation["user_id"] != user_id):
                raise PermissionException("respond to", "consultation")
            
            # Validasi input
            response_dto = self.validate_dto(ConsultationResponseCreateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(response_dto.dict())
            
            # Prepare response data
            response_data = {
                "consultation_id": consultation_id,
                "user_id": user_id,
                "message": sanitized_data["message"],
                "is_from_consultant": user.get("role") in ["admin", "consultant"],
                "attachments": sanitized_data.get("attachments", []),
                "created_at": datetime.now()
            }
            
            # Create response
            response = self.model.create_response(response_data)
            
            # Update consultation status if it's from consultant
            if response_data["is_from_consultant"] and consultation["status"] == "open":
                self.model.update_consultation(consultation_id, {
                    "status": "in_progress",
                    "updated_at": datetime.now()
                })
            
            # Log activity
            self.log_activity(user_id, "respond", "consultation", consultation_id, response_data)
            
            return self.create_success_response(
                data=response,
                message="Respons berhasil dibuat"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal membuat respons",
                code="CREATE_RESPONSE_ERROR"
            )
    
    def assign_consultation(
        self, 
        consultation_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Assign konsultasi ke konsultan"""
        try:
            # Check permission (only admin can assign)
            user = self.user_model.find_by_id(user_id)
            if not user or user.get("role") != "admin":
                raise PermissionException("assign", "consultation")
            
            # Check if consultation exists
            consultation = self.model.find_by_id(consultation_id)
            if not consultation:
                raise NotFoundException("Consultation", consultation_id)
            
            # Validasi input
            assign_dto = self.validate_dto(ConsultationAssignDTO, data)
            
            # Check if consultant exists
            consultant = self.user_model.find_by_id(assign_dto.consultant_id)
            if not consultant or consultant.get("role") != "consultant":
                raise NotFoundException("Consultant", assign_dto.consultant_id)
            
            # Update consultation
            update_data = {
                "assigned_to": assign_dto.consultant_id,
                "status": "assigned",
                "updated_at": datetime.now()
            }
            
            updated_consultation = self.model.update_consultation(consultation_id, update_data)
            
            # Log activity
            self.log_activity(user_id, "assign", "consultation", consultation_id, update_data)
            
            response_data = ConsultationResponseDTO(**updated_consultation)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Konsultasi berhasil di-assign"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal meng-assign konsultasi",
                code="ASSIGN_CONSULTATION_ERROR"
            )
    
    def update_status(
        self, 
        consultation_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Update status konsultasi"""
        try:
            # Check if consultation exists
            consultation = self.model.find_by_id(consultation_id)
            if not consultation:
                raise NotFoundException("Consultation", consultation_id)
            
            # Check permission
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            # Only admin, consultant, or consultation owner can update status
            if (user.get("role") not in ["admin", "consultant"] and 
                consultation["user_id"] != user_id):
                raise PermissionException("update status of", "consultation")
            
            # Validasi input
            status_dto = self.validate_dto(ConsultationStatusUpdateDTO, data)
            
            # Prepare update data
            update_data = {
                "status": status_dto.status,
                "updated_at": datetime.now()
            }
            
            # Add resolution if status is closed
            if status_dto.status == "closed" and status_dto.resolution:
                update_data["resolution"] = status_dto.resolution
                update_data["closed_at"] = datetime.now()
            
            # Update consultation
            updated_consultation = self.model.update_consultation(consultation_id, update_data)
            
            # Log activity
            self.log_activity(user_id, "update_status", "consultation", consultation_id, update_data)
            
            response_data = ConsultationResponseDTO(**updated_consultation)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Status konsultasi berhasil diperbarui"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memperbarui status konsultasi",
                code="UPDATE_STATUS_ERROR"
            )
    
    def rate_consultation(
        self, 
        consultation_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Berikan rating untuk konsultasi"""
        try:
            # Check if consultation exists
            consultation = self.model.find_by_id(consultation_id)
            if not consultation:
                raise NotFoundException("Consultation", consultation_id)
            
            # Check permission (only consultation owner can rate)
            if consultation["user_id"] != user_id:
                raise PermissionException("rate", "consultation")
            
            # Check if consultation is closed
            if consultation["status"] != "closed":
                raise ValidationException("Hanya konsultasi yang sudah selesai yang dapat diberi rating")
            
            # Validasi input
            satisfaction_dto = self.validate_dto(ConsultationSatisfactionDTO, data)
            
            # Prepare rating data
            rating_data = {
                "satisfaction_rating": satisfaction_dto.rating,
                "satisfaction_feedback": satisfaction_dto.feedback,
                "rated_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Update consultation
            updated_consultation = self.model.update_consultation(consultation_id, rating_data)
            
            # Log activity
            self.log_activity(user_id, "rate", "consultation", consultation_id, rating_data)
            
            response_data = ConsultationResponseDTO(**updated_consultation)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Rating berhasil diberikan"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memberikan rating",
                code="RATE_CONSULTATION_ERROR"
            )
    
    def delete_consultation(self, consultation_id: str, user_id: str) -> SuccessResponseDTO:
        """Hapus konsultasi (soft delete)"""
        try:
            # Check if consultation exists
            consultation = self.model.find_by_id(consultation_id)
            if not consultation:
                raise NotFoundException("Consultation", consultation_id)
            
            # Check permission
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            # Only admin or consultation owner can delete
            if (user.get("role") != "admin" and consultation["user_id"] != user_id):
                raise PermissionException("delete", "consultation")
            
            # Soft delete consultation
            success = self.model.soft_delete_consultation(consultation_id)
            if not success:
                return self.create_error_response(
                    message="Gagal menghapus konsultasi",
                    code="DELETE_CONSULTATION_ERROR"
                )
            
            # Log activity
            self.log_activity(user_id, "delete", "consultation", consultation_id)
            
            return self.create_success_response(
                data={"id": consultation_id},
                message="Konsultasi berhasil dihapus"
            )
            
        except (NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal menghapus konsultasi",
                code="DELETE_CONSULTATION_ERROR"
            )
    
    def get_consultation_stats(
        self, 
        user_id: str = None,
        consultant_id: str = None
    ) -> SuccessResponseDTO:
        """Mendapatkan statistik konsultasi"""
        try:
            # Check permission for global stats
            if not user_id and not consultant_id:
                # Global stats - only admin can access
                user = self.user_model.find_by_id(user_id)
                if not user or user.get("role") != "admin":
                    raise PermissionException("view", "global consultation statistics")
            
            stats = self.model.get_consultation_stats(user_id, consultant_id)
            response_data = ConsultationStatsDTO(**stats)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Statistik konsultasi berhasil diambil"
            )
            
        except PermissionException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil statistik konsultasi",
                code="CONSULTATION_STATS_ERROR"
            )
    
    def get_analytics(
        self, 
        user_id: str,
        days: int = 30
    ) -> SuccessResponseDTO:
        """Mendapatkan analitik konsultasi"""
        try:
            # Check permission (only admin can access analytics)
            user = self.user_model.find_by_id(user_id)
            if not user or user.get("role") != "admin":
                raise PermissionException("view", "consultation analytics")
            
            analytics = self.model.get_consultation_analytics(days)
            response_data = ConsultationAnalyticsDTO(**analytics)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Analitik konsultasi berhasil diambil"
            )
            
        except PermissionException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil analitik konsultasi",
                code="CONSULTATION_ANALYTICS_ERROR"
            )