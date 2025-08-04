from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import secrets
from models.application import ApplicationModel
from models.pesantren import PesantrenModel
from models.user import UserModel
from dto.application_dto import (
    ApplicationCreateDTO,
    ApplicationUpdateDTO,
    ApplicationResponseDTO,
    ApplicationSummaryDTO,
    ApplicationSearchDTO,
    ApplicationFilterDTO,
    ApplicationStatsDTO,
    ApplicationStatusUpdateDTO,
    ApplicationInterviewDTO,
    ApplicationPaymentDTO,
    ApplicationDocumentDTO,
    StudentDataDTO,
    ParentDataDTO
)
from dto.base_dto import PaginationDTO, PaginatedResponseDTO, SuccessResponseDTO
from .base_service import BaseService
from core.exceptions import NotFoundException, DuplicateException, ValidationException, PermissionException

class ApplicationService(BaseService[ApplicationCreateDTO, ApplicationModel]):
    """Service untuk mengelola pendaftaran pesantren"""
    
    def __init__(self):
        super().__init__(ApplicationModel)
        self.pesantren_model = PesantrenModel()
        self.user_model = UserModel()
    
    def get_resource_name(self) -> str:
        return "Application"
    
    def create_application(self, data: Dict[str, Any], user_id: str) -> SuccessResponseDTO:
        """Membuat pendaftaran baru"""
        try:
            # Validasi input
            application_dto = self.validate_dto(ApplicationCreateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(application_dto.dict())
            
            # Check if pesantren exists
            pesantren = self.pesantren_model.find_by_id(sanitized_data["pesantren_id"])
            if not pesantren:
                raise NotFoundException("Pesantren", sanitized_data["pesantren_id"])
            
            # Check if user exists
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            # Check if user already has active application for this pesantren
            existing_application = self.model.find_one({
                "pesantren_id": sanitized_data["pesantren_id"],
                "user_id": user_id,
                "status": {"$in": ["pending", "under_review", "interview_scheduled", "accepted"]}
            })
            if existing_application:
                raise DuplicateException("Application", "pesantren_id + user_id", f"{sanitized_data['pesantren_id']}+{user_id}")
            
            # Generate application number
            application_number = self._generate_application_number()
            
            # Prepare application data
            application_data = {
                "application_number": application_number,
                "pesantren_id": sanitized_data["pesantren_id"],
                "user_id": user_id,
                "academic_year": sanitized_data["academic_year"],
                "program_type": sanitized_data["program_type"],
                "student_data": sanitized_data["student_data"],
                "parent_data": sanitized_data["parent_data"],
                "previous_education": sanitized_data.get("previous_education"),
                "motivation": sanitized_data.get("motivation"),
                "special_needs": sanitized_data.get("special_needs"),
                "emergency_contact": sanitized_data.get("emergency_contact"),
                "status": "pending",
                "submission_date": datetime.now(),
                "documents": [],
                "status_history": [{
                    "status": "pending",
                    "changed_by": user_id,
                    "changed_at": datetime.now(),
                    "notes": "Pendaftaran dibuat"
                }],
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Create application
            application = self.model.create_application(application_data)
            
            # Update pesantren application stats
            self.pesantren_model.update_application_stats(sanitized_data["pesantren_id"])
            
            # Log activity
            self.log_activity(user_id, "create", "application", application["_id"], application_data)
            
            # Convert to response DTO
            response_data = ApplicationResponseDTO(**application)
            
            return self.create_success_response(
                data=response_data.dict(),
                message=f"Pendaftaran berhasil dibuat dengan nomor {application_number}"
            )
            
        except (ValidationException, NotFoundException, DuplicateException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal membuat pendaftaran",
                code="CREATE_APPLICATION_ERROR"
            )
    
    def get_application_by_id(self, application_id: str, user_id: str) -> SuccessResponseDTO:
        """Mendapatkan pendaftaran berdasarkan ID"""
        try:
            application = self.model.get_application_with_details(application_id)
            if not application:
                raise NotFoundException("Application", application_id)
            
            # Check permission (user can only see their own application, admin/pesantren can see all)
            user = self.user_model.find_by_id(user_id)
            if (application["user_id"] != user_id and 
                user.get("role") not in ["admin", "pesantren_admin"]):
                raise PermissionException("view", "application")
            
            response_data = ApplicationResponseDTO(**application)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Pendaftaran berhasil diambil"
            )
            
        except (NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil pendaftaran",
                code="GET_APPLICATION_ERROR"
            )
    
    def get_applications_list(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[ApplicationSearchDTO] = None,
        filters: Optional[ApplicationFilterDTO] = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan daftar semua pendaftaran dengan paginasi, pencarian, dan filter"""
        try:
            # Validate pagination
            pagination_dto = PaginationDTO(page=page, limit=limit)
            
            # Build query
            query = {}
            
            # Apply search
            if search and search.query:
                query["$or"] = [
                    {"application_number": {"$regex": search.query, "$options": "i"}},
                    {"student_data.full_name": {"$regex": search.query, "$options": "i"}},
                    {"student_data.email": {"$regex": search.query, "$options": "i"}}
                ]
            
            # Apply filters
            if filters:
                if filters.pesantren_id:
                    query["pesantren_id"] = filters.pesantren_id
                if filters.user_id:
                    query["user_id"] = filters.user_id
                if filters.status:
                    query["status"] = filters.status
                if filters.application_type:
                    query["application_type"] = filters.application_type
                if filters.submitted_from:
                    query["submission_date"] = {"$gte": filters.submitted_from}
                if filters.submitted_to:
                    query.setdefault("submission_date", {})["$lte"] = filters.submitted_to
                if filters.interview_scheduled is not None:
                    if filters.interview_scheduled:
                        query["interview_date"] = {"$exists": True, "$ne": None}
                    else:
                        query["$or"] = [
                            {"interview_date": {"$exists": False}},
                            {"interview_date": None}
                        ]
            
            # Calculate skip
            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            # Get applications with details
            applications = self.model.get_applications_with_pagination(
                query=query,
                skip=skip,
                limit=pagination_dto.limit,
                sort=[("created_at", -1)]
            )
            
            # Get total count
            total = self.model.count_documents(query)
            
            # Convert to response DTOs
            response_data = [ApplicationResponseDTO(**app).dict() for app in applications]
            
            return PaginatedResponseDTO(
                data=response_data,
                pagination={
                    "page": pagination_dto.page,
                    "limit": pagination_dto.limit,
                    "total": total,
                    "pages": (total + pagination_dto.limit - 1) // pagination_dto.limit
                },
                message="Daftar pendaftaran berhasil diambil"
            )
            
        except ValidationException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil daftar pendaftaran",
                code="GET_APPLICATIONS_LIST_ERROR"
            )
    
    def get_applications_by_user(
        self,
        user_id: str,
        filter_params: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None,
        current_user_id: str = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan pendaftaran berdasarkan pengguna"""
        try:
            # Check permission
            if user_id != current_user_id:
                current_user = self.user_model.find_by_id(current_user_id)
                if not current_user or current_user.get("role") != "admin":
                    raise PermissionException("view", "user applications")
            
            # Check if user exists
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            # Validate DTOs
            filter_dto = None
            if filter_params:
                filter_dto = self.validate_dto(ApplicationFilterDTO, filter_params)
            
            pagination_dto = PaginationDTO(**(pagination or {}))
            
            # Build query
            query = {"user_id": user_id}
            
            # Apply filters
            if filter_dto:
                if filter_dto.status:
                    query["status"] = filter_dto.status
                if filter_dto.academic_year:
                    query["academic_year"] = filter_dto.academic_year
                if filter_dto.program_type:
                    query["program_type"] = filter_dto.program_type
                if filter_dto.submitted_from:
                    query["submission_date"] = {"$gte": filter_dto.submitted_from}
                if filter_dto.submitted_to:
                    query.setdefault("submission_date", {})["$lte"] = filter_dto.submitted_to
            
            # Get data with pagination
            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            applications = self.model.get_applications_by_user(
                user_id=user_id,
                query=query,
                skip=skip,
                limit=pagination_dto.limit
            )
            
            total = self.model.count_documents(query)
            
            # Convert to response DTOs
            response_data = [ApplicationSummaryDTO(**app).dict() for app in applications]
            
            return self.create_paginated_response(
                data=response_data,
                pagination=pagination_dto,
                total=total,
                message="Pendaftaran pengguna berhasil diambil"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil pendaftaran pengguna",
                code="GET_USER_APPLICATIONS_ERROR"
            )
    
    def get_applications_by_pesantren(
        self,
        pesantren_id: str,
        search_params: Optional[Dict[str, Any]] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None,
        current_user_id: str = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan pendaftaran berdasarkan pesantren"""
        try:
            # Check permission
            current_user = self.user_model.find_by_id(current_user_id)
            if not current_user or current_user.get("role") not in ["admin", "pesantren_admin"]:
                raise PermissionException("view", "pesantren applications")
            
            # Check if pesantren exists
            pesantren = self.pesantren_model.find_by_id(pesantren_id)
            if not pesantren:
                raise NotFoundException("Pesantren", pesantren_id)
            
            # Validate DTOs
            search_dto = None
            if search_params:
                search_dto = self.validate_dto(ApplicationSearchDTO, search_params)
            
            filter_dto = None
            if filter_params:
                filter_dto = self.validate_dto(ApplicationFilterDTO, filter_params)
            
            pagination_dto = PaginationDTO(**(pagination or {}))
            
            # Build query
            query = {"pesantren_id": pesantren_id}
            
            # Apply search
            if search_dto and search_dto.query:
                query["$or"] = [
                    {"application_number": {"$regex": search_dto.query, "$options": "i"}},
                    {"student_data.full_name": {"$regex": search_dto.query, "$options": "i"}},
                    {"student_data.email": {"$regex": search_dto.query, "$options": "i"}}
                ]
            
            # Apply filters
            if filter_dto:
                if filter_dto.status:
                    query["status"] = filter_dto.status
                if filter_dto.academic_year:
                    query["academic_year"] = filter_dto.academic_year
                if filter_dto.program_type:
                    query["program_type"] = filter_dto.program_type
                if filter_dto.submitted_from:
                    query["submission_date"] = {"$gte": filter_dto.submitted_from}
                if filter_dto.submitted_to:
                    query.setdefault("submission_date", {})["$lte"] = filter_dto.submitted_to
            
            # Get data with pagination
            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            # Determine sort order
            sort_order = []
            if search_dto and search_dto.sort_by:
                if search_dto.sort_by == "date":
                    sort_order.append(("submission_date", -1 if search_dto.sort_order == "desc" else 1))
                elif search_dto.sort_by == "name":
                    sort_order.append(("student_data.full_name", 1 if search_dto.sort_order == "asc" else -1))
                elif search_dto.sort_by == "status":
                    sort_order.append(("status", 1 if search_dto.sort_order == "asc" else -1))
            else:
                sort_order.append(("submission_date", -1))  # Default: newest first
            
            applications = self.model.get_applications_by_pesantren(
                pesantren_id=pesantren_id,
                query=query,
                skip=skip,
                limit=pagination_dto.limit,
                sort=sort_order
            )
            
            total = self.model.count_documents(query)
            
            # Convert to response DTOs
            response_data = [ApplicationSummaryDTO(**app).dict() for app in applications]
            
            return self.create_paginated_response(
                data=response_data,
                pagination=pagination_dto,
                total=total,
                message="Pendaftaran pesantren berhasil diambil"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil pendaftaran pesantren",
                code="GET_PESANTREN_APPLICATIONS_ERROR"
            )
    
    def update_application(
        self, 
        application_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Update pendaftaran"""
        try:
            # Check if application exists
            application = self.model.find_by_id(application_id)
            if not application:
                raise NotFoundException("Application", application_id)
            
            # Check permission (only application owner can update, and only if status allows)
            if application["user_id"] != user_id:
                raise PermissionException("update", "application")
            
            # Check if application can be updated
            if application["status"] not in ["pending", "under_review"]:
                return self.create_error_response(
                    message="Pendaftaran tidak dapat diubah pada status saat ini",
                    code="APPLICATION_UPDATE_NOT_ALLOWED"
                )
            
            # Validasi input
            update_dto = self.validate_dto(ApplicationUpdateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(update_dto.dict(exclude_unset=True))
            
            # Add update metadata
            sanitized_data["updated_at"] = datetime.now()
            
            # Update application
            updated_application = self.model.update_application(application_id, sanitized_data)
            
            # Log activity
            self.log_activity(user_id, "update", "application", application_id, sanitized_data)
            
            response_data = ApplicationResponseDTO(**updated_application)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Pendaftaran berhasil diperbarui"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memperbarui pendaftaran",
                code="UPDATE_APPLICATION_ERROR"
            )
    
    def update_application_status(
        self, 
        application_id: str, 
        data: Dict[str, Any], 
        admin_id: str
    ) -> SuccessResponseDTO:
        """Update status pendaftaran (admin/pesantren only)"""
        try:
            # Check permission
            admin = self.user_model.find_by_id(admin_id)
            if not admin or admin.get("role") not in ["admin", "pesantren_admin"]:
                raise PermissionException("update_status", "application")
            
            # Check if application exists
            application = self.model.find_by_id(application_id)
            if not application:
                raise NotFoundException("Application", application_id)
            
            # Validasi input
            status_dto = self.validate_dto(ApplicationStatusUpdateDTO, data)
            
            # Validate status transition
            if not self._is_valid_status_transition(application["status"], status_dto.status):
                return self.create_error_response(
                    message=f"Transisi status dari {application['status']} ke {status_dto.status} tidak valid",
                    code="INVALID_STATUS_TRANSITION"
                )
            
            # Prepare status update data
            status_data = {
                "status": status_dto.status,
                "updated_at": datetime.now()
            }
            
            # Add status to history
            status_history_entry = {
                "status": status_dto.status,
                "changed_by": admin_id,
                "changed_at": datetime.now(),
                "notes": status_dto.notes
            }
            
            # Update application
            updated_application = self.model.update_application_status(
                application_id, 
                status_data, 
                status_history_entry
            )
            
            # Update pesantren stats if status changed to accepted/rejected
            if status_dto.status in ["accepted", "rejected"]:
                self.pesantren_model.update_application_stats(application["pesantren_id"])
            
            # Log activity
            self.log_activity(admin_id, "update_status", "application", application_id, {
                "old_status": application["status"],
                "new_status": status_dto.status,
                "notes": status_dto.notes
            })
            
            response_data = ApplicationResponseDTO(**updated_application)
            
            return self.create_success_response(
                data=response_data.dict(),
                message=f"Status pendaftaran berhasil diubah menjadi {status_dto.status}"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengubah status pendaftaran",
                code="UPDATE_APPLICATION_STATUS_ERROR"
            )
    
    def schedule_interview(
        self, 
        application_id: str, 
        data: Dict[str, Any], 
        admin_id: str
    ) -> SuccessResponseDTO:
        """Jadwalkan wawancara"""
        try:
            # Check permission
            admin = self.user_model.find_by_id(admin_id)
            if not admin or admin.get("role") not in ["admin", "pesantren_admin"]:
                raise PermissionException("schedule_interview", "application")
            
            # Check if application exists
            application = self.model.find_by_id(application_id)
            if not application:
                raise NotFoundException("Application", application_id)
            
            # Check if application status allows interview scheduling
            if application["status"] not in ["under_review", "interview_scheduled"]:
                return self.create_error_response(
                    message="Wawancara hanya dapat dijadwalkan untuk pendaftaran yang sedang direview",
                    code="INTERVIEW_SCHEDULE_NOT_ALLOWED"
                )
            
            # Validasi input
            interview_dto = self.validate_dto(ApplicationInterviewDTO, data)
            
            # Prepare interview data
            interview_data = {
                "interview_date": interview_dto.interview_date,
                "interview_time": interview_dto.interview_time,
                "interview_location": interview_dto.interview_location,
                "interview_type": interview_dto.interview_type,
                "interviewer": interview_dto.interviewer,
                "interview_notes": interview_dto.notes,
                "scheduled_by": admin_id,
                "scheduled_at": datetime.now()
            }
            
            # Update application with interview details
            updated_application = self.model.schedule_interview(application_id, interview_data)
            
            # Update status to interview_scheduled if not already
            if application["status"] != "interview_scheduled":
                status_history_entry = {
                    "status": "interview_scheduled",
                    "changed_by": admin_id,
                    "changed_at": datetime.now(),
                    "notes": "Wawancara dijadwalkan"
                }
                self.model.update_application_status(
                    application_id,
                    {"status": "interview_scheduled"},
                    status_history_entry
                )
            
            # Log activity
            self.log_activity(admin_id, "schedule_interview", "application", application_id, interview_data)
            
            response_data = ApplicationResponseDTO(**updated_application)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Wawancara berhasil dijadwalkan"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal menjadwalkan wawancara",
                code="SCHEDULE_INTERVIEW_ERROR"
            )
    
    def upload_document(
        self, 
        application_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Upload dokumen pendaftaran"""
        try:
            # Check if application exists
            application = self.model.find_by_id(application_id)
            if not application:
                raise NotFoundException("Application", application_id)
            
            # Check permission (only application owner can upload)
            if application["user_id"] != user_id:
                raise PermissionException("upload_document", "application")
            
            # Validasi input
            document_dto = self.validate_dto(ApplicationDocumentDTO, data)
            
            # Prepare document data
            document_data = {
                "document_type": document_dto.document_type,
                "file_name": document_dto.file_name,
                "file_path": document_dto.file_path,
                "file_size": document_dto.file_size,
                "uploaded_by": user_id,
                "uploaded_at": datetime.now()
            }
            
            # Add document to application
            success = self.model.add_document(application_id, document_data)
            if not success:
                return self.create_error_response(
                    message="Gagal mengunggah dokumen",
                    code="UPLOAD_DOCUMENT_ERROR"
                )
            
            # Log activity
            self.log_activity(user_id, "upload_document", "application", application_id, document_data)
            
            return self.create_success_response(
                data={"id": application_id, "document": document_data},
                message="Dokumen berhasil diunggah"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengunggah dokumen",
                code="UPLOAD_DOCUMENT_ERROR"
            )
    
    def get_application_stats(
        self, 
        pesantren_id: Optional[str] = None,
        current_user_id: str = None
    ) -> SuccessResponseDTO:
        """Mendapatkan statistik pendaftaran"""
        try:
            # Check permission for global stats
            if not pesantren_id and current_user_id:
                user = self.user_model.find_by_id(current_user_id)
                if not user or user.get("role") not in ["admin"]:
                    raise PermissionException("view", "global application statistics")
            
            stats = self.model.get_application_stats(pesantren_id)
            response_data = ApplicationStatsDTO(**stats)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Statistik pendaftaran berhasil diambil"
            )
            
        except PermissionException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil statistik pendaftaran",
                code="APPLICATION_STATS_ERROR"
            )
    
    def _generate_application_number(self) -> str:
        """Generate unique application number"""
        year = datetime.now().year
        month = datetime.now().month
        
        # Count applications this month
        start_of_month = datetime(year, month, 1)
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1)
        else:
            end_of_month = datetime(year, month + 1, 1)
        
        count = self.model.count_documents({
            "created_at": {
                "$gte": start_of_month,
                "$lt": end_of_month
            }
        })
        
        return f"APP{year}{month:02d}{count + 1:04d}"
    
    def _is_valid_status_transition(self, current_status: str, new_status: str) -> bool:
        """Validate status transition"""
        valid_transitions = {
            "pending": ["under_review", "rejected"],
            "under_review": ["interview_scheduled", "accepted", "rejected"],
            "interview_scheduled": ["accepted", "rejected"],
            "accepted": ["enrolled", "cancelled"],
            "rejected": [],
            "enrolled": ["cancelled"],
            "cancelled": []
        }
        
        return new_status in valid_transitions.get(current_status, [])