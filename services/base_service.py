from typing import Dict, List, Optional, Any, Type, TypeVar, Generic
from abc import ABC, abstractmethod
from datetime import datetime
from pydantic import BaseModel, ValidationError
from core.db import DatabaseConfig
from core.exceptions import (
    ServiceException,
    ValidationException,
    NotFoundException,
    DuplicateException,
    PermissionException
)
from dto.base_dto import (
    PaginationDTO,
    PaginatedResponseDTO,
    SuccessResponseDTO,
    ErrorResponseDTO,
    ValidationErrorResponseDTO
)

T = TypeVar('T', bound=BaseModel)
M = TypeVar('M')  # Model type

class BaseService(Generic[T, M], ABC):
    """Base service class dengan fungsionalitas umum"""
    
    def __init__(self, model_class: Type[M]):
        self.db = DatabaseConfig()
        self.model = model_class()
        
    def validate_dto(self, dto_class: Type[T], data: Dict[str, Any]) -> T:
        """Validasi data menggunakan DTO"""
        try:
            return dto_class(**data)
        except ValidationError as e:
            errors = []
            for error in e.errors():
                errors.append({
                    "field": ".".join(str(x) for x in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"]
                })
            raise ValidationException(errors)
    
    def create_success_response(
        self, 
        data: Any, 
        message: str = "Operasi berhasil",
        meta: Optional[Dict[str, Any]] = None
    ) -> SuccessResponseDTO:
        """Membuat response sukses"""
        return SuccessResponseDTO(
            success=True,
            message=message,
            data=data,
            meta=meta or {},
            timestamp=datetime.now()
        )
    
    def create_error_response(
        self, 
        message: str, 
        code: str = "ERROR",
        details: Optional[Dict[str, Any]] = None
    ) -> ErrorResponseDTO:
        """Membuat response error"""
        return ErrorResponseDTO(
            success=False,
            error=message,
            error_code=code,
            details=details or {},
            timestamp=datetime.now()
        )
    
    def create_validation_error_response(
        self, 
        errors: List[Dict[str, Any]]
    ) -> ValidationErrorResponseDTO:
        """Membuat response validation error"""
        return ValidationErrorResponseDTO(
            success=False,
            error="Validation failed",
            error_code="VALIDATION_ERROR",
            validation_errors=errors,
            timestamp=datetime.now()
        )
    
    def create_paginated_response(
        self,
        data: List[Any],
        pagination: PaginationDTO,
        total: int,
        message: str = "Data berhasil diambil"
    ) -> PaginatedResponseDTO:
        """Membuat response dengan paginasi"""
        total_pages = (total + pagination.limit - 1) // pagination.limit
        
        return PaginatedResponseDTO(
            data=data,
            pagination=PaginationDTO(
                page=pagination.page,
                limit=pagination.limit,
                total=total,
                total_pages=total_pages,
                has_next=pagination.page < total_pages,
                has_prev=pagination.page > 1
            )
        )
    
    def handle_service_exception(self, e: ServiceException) -> ErrorResponseDTO:
        """Handle service exceptions"""
        if isinstance(e, ValidationException):
            return self.create_validation_error_response(e.errors)
        
        return self.create_error_response(
            message=e.message,
            code=e.code
        )
    
    def check_exists(self, resource_id: str, resource_name: str) -> None:
        """Check if resource exists"""
        if not self.model.find_by_id(resource_id):
            raise NotFoundException(resource_name, resource_id)
    
    def check_permission(self, user_id: str, action: str, resource: str, resource_data: Optional[Dict] = None) -> None:
        """Check user permission for action"""
        # Implementasi basic permission check
        # Bisa diperluas sesuai kebutuhan authorization
        pass
    
    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data"""
        sanitized = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Basic sanitization
                sanitized[key] = value.strip()
            else:
                sanitized[key] = value
        return sanitized
    
    def log_activity(self, user_id: str, action: str, resource: str, resource_id: str, details: Optional[Dict] = None):
        """Log user activity"""
        # Implementasi logging activity
        # Bisa menggunakan database atau external logging service
        activity_log = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details or {},
            "timestamp": datetime.now(),
            "ip_address": None,  # Bisa diambil dari request context
            "user_agent": None   # Bisa diambil dari request context
        }
        # TODO: Implement actual logging
        print(f"Activity Log: {activity_log}")
    
    @abstractmethod
    def get_resource_name(self) -> str:
        """Get resource name for logging and error messages"""
        pass
    
    def close_connection(self):
        """Close database connection"""
        self.db.close_connection()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()