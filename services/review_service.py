from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from models.review import ReviewModel
from models.pesantren import PesantrenModel
from models.user import UserModel
from dto.review_dto import (
    ReviewCreateDTO,
    ReviewUpdateDTO,
    ReviewResponseDTO,
    ReviewSummaryDTO,
    ReviewSearchDTO,
    ReviewFilterDTO,
    ReviewStatsDTO,
    ReviewModerationDTO,
    ReviewHelpfulDTO,
    ReviewReportDTO,
    ReviewAnalyticsDTO,
    ReviewBulkActionDTO
)
from dto.base_dto import PaginationDTO, PaginatedResponseDTO, SuccessResponseDTO
from .base_service import BaseService, NotFoundException, DuplicateException, ValidationException, PermissionException

class ReviewService(BaseService[ReviewCreateDTO, ReviewModel]):
    """Service untuk mengelola ulasan pesantren"""
    
    def __init__(self):
        super().__init__(ReviewModel)
        self.pesantren_model = PesantrenModel()
        self.user_model = UserModel()
    
    def get_resource_name(self) -> str:
        return "Review"
    
    def create_review(self, data: Dict[str, Any], user_id: str) -> SuccessResponseDTO:
        """Membuat ulasan baru"""
        try:
            # Validasi input
            review_dto = self.validate_dto(ReviewCreateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(review_dto.dict())
            
            # Check if pesantren exists
            pesantren = self.pesantren_model.find_by_id(sanitized_data["pesantren_id"])
            if not pesantren:
                raise NotFoundException("Pesantren", sanitized_data["pesantren_id"])
            
            # Check if user exists
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            # Check if user already reviewed this pesantren
            existing_review = self.model.find_one({
                "pesantren_id": sanitized_data["pesantren_id"],
                "user_id": user_id,
                "is_deleted": False
            })
            if existing_review:
                raise DuplicateException("Review", "pesantren_id + user_id", f"{sanitized_data['pesantren_id']}+{user_id}")
            
            # Prepare review data
            review_data = {
                "pesantren_id": sanitized_data["pesantren_id"],
                "user_id": user_id,
                "rating": sanitized_data["rating"],
                "title": sanitized_data["title"],
                "content": sanitized_data["content"],
                "pros": sanitized_data.get("pros", []),
                "cons": sanitized_data.get("cons", []),
                "recommendation": sanitized_data.get("recommendation"),
                "visit_date": sanitized_data.get("visit_date"),
                "is_anonymous": sanitized_data.get("is_anonymous", False),
                "status": "pending",  # Default to pending for moderation
                "helpful_count": 0,
                "not_helpful_count": 0,
                "report_count": 0,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Create review
            review = self.model.create_review(review_data)
            
            # Update pesantren review stats
            self.pesantren_model.update_review_stats(sanitized_data["pesantren_id"])
            
            # Log activity
            self.log_activity(user_id, "create", "review", review["_id"], review_data)
            
            # Convert to response DTO
            response_data = ReviewResponseDTO(**review)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Ulasan berhasil dibuat dan sedang menunggu moderasi"
            )
            
        except (ValidationException, NotFoundException, DuplicateException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal membuat ulasan",
                code="CREATE_REVIEW_ERROR"
            )
    
    def get_review_by_id(self, review_id: str) -> SuccessResponseDTO:
        """Mendapatkan ulasan berdasarkan ID"""
        try:
            review = self.model.get_review_with_details(review_id)
            if not review:
                raise NotFoundException("Review", review_id)
            
            response_data = ReviewResponseDTO(**review)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Ulasan berhasil diambil"
            )
            
        except NotFoundException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil ulasan",
                code="GET_REVIEW_ERROR"
            )
    
    def get_reviews_by_pesantren(
        self,
        pesantren_id: str,
        search_params: Optional[Dict[str, Any]] = None,
        filter_params: Optional[Dict[str, Any]] = None,
        pagination: Optional[Dict[str, Any]] = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan ulasan berdasarkan pesantren"""
        try:
            # Check if pesantren exists
            pesantren = self.pesantren_model.find_by_id(pesantren_id)
            if not pesantren:
                raise NotFoundException("Pesantren", pesantren_id)
            
            # Validate DTOs
            search_dto = None
            if search_params:
                search_dto = self.validate_dto(ReviewSearchDTO, search_params)
            
            filter_dto = None
            if filter_params:
                filter_dto = self.validate_dto(ReviewFilterDTO, filter_params)
            
            pagination_dto = PaginationDTO(**(pagination or {}))
            
            # Build query
            query = {
                "pesantren_id": pesantren_id,
                "is_deleted": False,
                "status": "approved"  # Only show approved reviews
            }
            
            # Apply search
            if search_dto and search_dto.query:
                query["$or"] = [
                    {"title": {"$regex": search_dto.query, "$options": "i"}},
                    {"content": {"$regex": search_dto.query, "$options": "i"}}
                ]
            
            # Apply filters
            if filter_dto:
                if filter_dto.rating:
                    query["rating"] = filter_dto.rating
                if filter_dto.min_rating:
                    query["rating"] = {"$gte": filter_dto.min_rating}
                if filter_dto.max_rating:
                    query.setdefault("rating", {})["$lte"] = filter_dto.max_rating
                if filter_dto.has_recommendation is not None:
                    if filter_dto.has_recommendation:
                        query["recommendation"] = {"$ne": None}
                    else:
                        query["recommendation"] = None
                if filter_dto.created_from:
                    query["created_at"] = {"$gte": filter_dto.created_from}
                if filter_dto.created_to:
                    query.setdefault("created_at", {})["$lte"] = filter_dto.created_to
            
            # Get data with pagination
            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            # Determine sort order
            sort_order = []
            if search_dto and search_dto.sort_by:
                if search_dto.sort_by == "rating":
                    sort_order.append(("rating", -1 if search_dto.sort_order == "desc" else 1))
                elif search_dto.sort_by == "helpful":
                    sort_order.append(("helpful_count", -1 if search_dto.sort_order == "desc" else 1))
                elif search_dto.sort_by == "date":
                    sort_order.append(("created_at", -1 if search_dto.sort_order == "desc" else 1))
            else:
                sort_order.append(("created_at", -1))  # Default: newest first
            
            reviews = self.model.get_reviews_by_pesantren(
                pesantren_id=pesantren_id,
                query=query,
                skip=skip,
                limit=pagination_dto.limit,
                sort=sort_order
            )
            
            total = self.model.count_documents(query)
            
            # Convert to response DTOs
            response_data = [ReviewResponseDTO(**review).dict() for review in reviews]
            
            return self.create_paginated_response(
                data=response_data,
                pagination=pagination_dto,
                total=total,
                message="Ulasan pesantren berhasil diambil"
            )
            
        except (ValidationException, NotFoundException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil ulasan pesantren",
                code="GET_PESANTREN_REVIEWS_ERROR"
            )
    
    def update_review(
        self, 
        review_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Update ulasan"""
        try:
            # Check if review exists
            review = self.model.find_by_id(review_id)
            if not review:
                raise NotFoundException("Review", review_id)
            
            # Check permission (only review owner can update)
            if review["user_id"] != user_id:
                raise PermissionException("update", "review")
            
            # Check if review can be updated (not if already approved and older than 24 hours)
            if (review["status"] == "approved" and 
                review["created_at"] < datetime.now() - timedelta(hours=24)):
                return self.create_error_response(
                    message="Ulasan yang sudah disetujui tidak dapat diubah setelah 24 jam",
                    code="REVIEW_UPDATE_EXPIRED"
                )
            
            # Validasi input
            update_dto = self.validate_dto(ReviewUpdateDTO, data)
            
            # Sanitize input
            sanitized_data = self.sanitize_input(update_dto.dict(exclude_unset=True))
            
            # Add update metadata
            sanitized_data["updated_at"] = datetime.now()
            
            # If content is updated, reset status to pending
            if any(key in sanitized_data for key in ["title", "content", "rating"]):
                sanitized_data["status"] = "pending"
            
            # Update review
            updated_review = self.model.update_review(review_id, sanitized_data)
            
            # Update pesantren review stats if rating changed
            if "rating" in sanitized_data:
                self.pesantren_model.update_review_stats(review["pesantren_id"])
            
            # Log activity
            self.log_activity(user_id, "update", "review", review_id, sanitized_data)
            
            response_data = ReviewResponseDTO(**updated_review)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Ulasan berhasil diperbarui"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal memperbarui ulasan",
                code="UPDATE_REVIEW_ERROR"
            )
    
    def delete_review(self, review_id: str, user_id: str) -> SuccessResponseDTO:
        """Hapus ulasan (soft delete)"""
        try:
            # Check if review exists
            review = self.model.find_by_id(review_id)
            if not review:
                raise NotFoundException("Review", review_id)
            
            # Check permission (only review owner or admin can delete)
            user = self.user_model.find_by_id(user_id)
            if review["user_id"] != user_id and user.get("role") != "admin":
                raise PermissionException("delete", "review")
            
            # Soft delete review
            success = self.model.soft_delete_review(review_id)
            if not success:
                return self.create_error_response(
                    message="Gagal menghapus ulasan",
                    code="DELETE_REVIEW_ERROR"
                )
            
            # Update pesantren review stats
            self.pesantren_model.update_review_stats(review["pesantren_id"])
            
            # Log activity
            self.log_activity(user_id, "delete", "review", review_id)
            
            return self.create_success_response(
                data={"id": review_id},
                message="Ulasan berhasil dihapus"
            )
            
        except (NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal menghapus ulasan",
                code="DELETE_REVIEW_ERROR"
            )
    
    def moderate_review(
        self, 
        review_id: str, 
        data: Dict[str, Any], 
        moderator_id: str
    ) -> SuccessResponseDTO:
        """Moderasi ulasan (admin only)"""
        try:
            # Check permission
            moderator = self.user_model.find_by_id(moderator_id)
            if not moderator or moderator.get("role") not in ["admin", "moderator"]:
                raise PermissionException("moderate", "review")
            
            # Check if review exists
            review = self.model.find_by_id(review_id)
            if not review:
                raise NotFoundException("Review", review_id)
            
            # Validasi input
            moderation_dto = self.validate_dto(ReviewModerationDTO, data)
            
            # Update review status
            moderation_data = {
                "status": moderation_dto.status,
                "moderation_notes": moderation_dto.notes,
                "moderated_by": moderator_id,
                "moderated_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            updated_review = self.model.update_review(review_id, moderation_data)
            
            # Update pesantren review stats if approved/rejected
            if moderation_dto.status in ["approved", "rejected"]:
                self.pesantren_model.update_review_stats(review["pesantren_id"])
            
            # Log activity
            self.log_activity(moderator_id, "moderate", "review", review_id, moderation_data)
            
            response_data = ReviewResponseDTO(**updated_review)
            
            return self.create_success_response(
                data=response_data.dict(),
                message=f"Ulasan berhasil {moderation_dto.status}"
            )
            
        except (ValidationException, NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal melakukan moderasi ulasan",
                code="MODERATE_REVIEW_ERROR"
            )
    
    def mark_helpful(
        self, 
        review_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Tandai ulasan sebagai bermanfaat/tidak bermanfaat"""
        try:
            # Check if review exists
            review = self.model.find_by_id(review_id)
            if not review:
                raise NotFoundException("Review", review_id)
            
            # Validasi input
            helpful_dto = self.validate_dto(ReviewHelpfulDTO, data)
            
            # Check if user already marked this review
            existing_mark = self.model.find_helpful_mark(review_id, user_id)
            
            if existing_mark:
                # Update existing mark
                success = self.model.update_helpful_mark(
                    review_id, 
                    user_id, 
                    helpful_dto.is_helpful
                )
            else:
                # Create new mark
                success = self.model.mark_helpful(
                    review_id, 
                    user_id, 
                    helpful_dto.is_helpful
                )
            
            if not success:
                return self.create_error_response(
                    message="Gagal menandai ulasan",
                    code="MARK_HELPFUL_ERROR"
                )
            
            # Get updated review
            updated_review = self.model.find_by_id(review_id)
            
            # Log activity
            self.log_activity(user_id, "mark_helpful", "review", review_id, {
                "is_helpful": helpful_dto.is_helpful
            })
            
            return self.create_success_response(
                data={
                    "id": review_id,
                    "helpful_count": updated_review["helpful_count"],
                    "not_helpful_count": updated_review["not_helpful_count"]
                },
                message="Ulasan berhasil ditandai"
            )
            
        except (ValidationException, NotFoundException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal menandai ulasan",
                code="MARK_HELPFUL_ERROR"
            )
    
    def report_review(
        self, 
        review_id: str, 
        data: Dict[str, Any], 
        user_id: str
    ) -> SuccessResponseDTO:
        """Laporkan ulasan"""
        try:
            # Check if review exists
            review = self.model.find_by_id(review_id)
            if not review:
                raise NotFoundException("Review", review_id)
            
            # Validasi input
            report_dto = self.validate_dto(ReviewReportDTO, data)
            
            # Check if user already reported this review
            existing_report = self.model.find_report(review_id, user_id)
            if existing_report:
                return self.create_error_response(
                    message="Anda sudah melaporkan ulasan ini",
                    code="ALREADY_REPORTED"
                )
            
            # Create report
            report_data = {
                "review_id": review_id,
                "user_id": user_id,
                "reason": report_dto.reason,
                "description": report_dto.description,
                "created_at": datetime.now()
            }
            
            success = self.model.report_review(report_data)
            if not success:
                return self.create_error_response(
                    message="Gagal melaporkan ulasan",
                    code="REPORT_REVIEW_ERROR"
                )
            
            # Log activity
            self.log_activity(user_id, "report", "review", review_id, report_data)
            
            return self.create_success_response(
                data={"id": review_id},
                message="Ulasan berhasil dilaporkan"
            )
            
        except (ValidationException, NotFoundException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal melaporkan ulasan",
                code="REPORT_REVIEW_ERROR"
            )
    
    def get_review_stats(
        self, 
        pesantren_id: Optional[str] = None,
        current_user_id: str = None
    ) -> SuccessResponseDTO:
        """Mendapatkan statistik ulasan"""
        try:
            # Check permission for global stats
            if not pesantren_id and current_user_id:
                user = self.user_model.find_by_id(current_user_id)
                if not user or user.get("role") not in ["admin", "moderator"]:
                    raise PermissionException("view", "global review statistics")
            
            stats = self.model.get_review_stats(pesantren_id)
            response_data = ReviewStatsDTO(**stats)
            
            return self.create_success_response(
                data=response_data.dict(),
                message="Statistik ulasan berhasil diambil"
            )
            
        except PermissionException as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil statistik ulasan",
                code="REVIEW_STATS_ERROR"
            )
    
    def get_user_reviews(
        self,
        user_id: str,
        pagination: Optional[Dict[str, Any]] = None,
        current_user_id: str = None
    ) -> PaginatedResponseDTO:
        """Mendapatkan ulasan pengguna"""
        try:
            # Check permission (user can only see their own reviews, admin can see all)
            if user_id != current_user_id:
                current_user = self.user_model.find_by_id(current_user_id)
                if not current_user or current_user.get("role") != "admin":
                    raise PermissionException("view", "user reviews")
            
            # Check if user exists
            user = self.user_model.find_by_id(user_id)
            if not user:
                raise NotFoundException("User", user_id)
            
            pagination_dto = PaginationDTO(**(pagination or {}))
            
            # Build query
            query = {
                "user_id": user_id,
                "is_deleted": False
            }
            
            # Get data with pagination
            skip = (pagination_dto.page - 1) * pagination_dto.limit
            
            reviews = self.model.get_user_reviews(
                user_id=user_id,
                skip=skip,
                limit=pagination_dto.limit
            )
            
            total = self.model.count_documents(query)
            
            # Convert to response DTOs
            response_data = [ReviewResponseDTO(**review).dict() for review in reviews]
            
            return self.create_paginated_response(
                data=response_data,
                pagination=pagination_dto,
                total=total,
                message="Ulasan pengguna berhasil diambil"
            )
            
        except (NotFoundException, PermissionException) as e:
            return self.handle_service_exception(e)
        except Exception as e:
            return self.create_error_response(
                message="Gagal mengambil ulasan pengguna",
                code="USER_REVIEWS_ERROR"
            )