from typing import Dict, List, Any

class ServiceException(Exception):
    """Base exception untuk services"""
    def __init__(self, message: str, code: str = "SERVICE_ERROR", status_code: int = 500):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)

class ValidationException(ServiceException):
    """Exception untuk validation errors"""
    def __init__(self, errors: List[Dict[str, Any]]):
        self.errors = errors
        super().__init__("Validation failed", "VALIDATION_ERROR", 400)

class NotFoundException(ServiceException):
    """Exception untuk resource not found"""
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} dengan ID {identifier} tidak ditemukan"
        super().__init__(message, "NOT_FOUND", 404)

class DuplicateException(ServiceException):
    """Exception untuk duplicate resource"""
    def __init__(self, resource: str, field: str, value: str):
        message = f"{resource} dengan {field} '{value}' sudah ada"
        super().__init__(message, "DUPLICATE_ERROR", 409)

class PermissionException(ServiceException):
    """Exception untuk permission denied"""
    def __init__(self, action: str, resource: str):
        message = f"Tidak memiliki izin untuk {action} {resource}"
        super().__init__(message, "PERMISSION_DENIED", 403)