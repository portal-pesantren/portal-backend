from typing import Dict, Any, Optional, Callable
from functools import wraps
import json
from datetime import datetime
from core.exceptions import ServiceException, ValidationException, NotFoundException, PermissionException
from dto.base_dto import PaginationDTO, ErrorResponseDTO

class BaseRouter:
    """Base router class untuk menyediakan fungsionalitas umum"""
    
    def __init__(self):
        self.routes = {}
    
    def handle_request(self, method: str, path: str, data: Dict[str, Any] = None, 
                      headers: Dict[str, str] = None, query_params: Dict[str, str] = None) -> Dict[str, Any]:
        """Handle HTTP request"""
        try:
            # Get route handler
            route_key = f"{method.upper()}:{path}"
            if route_key not in self.routes:
                return self.create_error_response(
                    message="Route not found",
                    status_code=404,
                    code="ROUTE_NOT_FOUND"
                )
            
            handler = self.routes[route_key]
            
            # Prepare request context
            request_context = {
                "method": method.upper(),
                "path": path,
                "data": data or {},
                "headers": headers or {},
                "query_params": query_params or {},
                "timestamp": datetime.now().isoformat()
            }
            
            # Execute handler
            response = handler(request_context)
            
            # Ensure response has proper structure
            if not isinstance(response, dict):
                return self.create_error_response(
                    message="Invalid response format",
                    status_code=500,
                    code="INVALID_RESPONSE"
                )
            
            # Add response metadata
            response["timestamp"] = datetime.now().isoformat()
            response["request_id"] = self.generate_request_id()
            
            return response
            
        except Exception as e:
            return self.handle_exception(e)
    
    def register_route(self, method: str, path: str, handler: Callable) -> None:
        """Register route handler"""
        route_key = f"{method.upper()}:{path}"
        self.routes[route_key] = handler
    
    def get(self, path: str):
        """Decorator untuk GET routes"""
        def decorator(handler):
            self.register_route("GET", path, handler)
            return handler
        return decorator
    
    def post(self, path: str):
        """Decorator untuk POST routes"""
        def decorator(handler):
            self.register_route("POST", path, handler)
            return handler
        return decorator
    
    def put(self, path: str):
        """Decorator untuk PUT routes"""
        def decorator(handler):
            self.register_route("PUT", path, handler)
            return handler
        return decorator
    
    def patch(self, path: str):
        """Decorator untuk PATCH routes"""
        def decorator(handler):
            self.register_route("PATCH", path, handler)
            return handler
        return decorator
    
    def delete(self, path: str):
        """Decorator untuk DELETE routes"""
        def decorator(handler):
            self.register_route("DELETE", path, handler)
            return handler
        return decorator
    
    def authenticate_required(self, handler: Callable) -> Callable:
        """Decorator untuk routes yang memerlukan autentikasi"""
        @wraps(handler)
        def wrapper(request_context: Dict[str, Any]) -> Dict[str, Any]:
            # Extract token from headers
            auth_header = request_context["headers"].get("Authorization", "")
            if not auth_header.startswith("Bearer "):
                return self.create_error_response(
                    message="Token autentikasi diperlukan",
                    status_code=401,
                    code="AUTHENTICATION_REQUIRED"
                )
            
            token = auth_header[7:]  # Remove "Bearer " prefix
            
            # Validate token (implement your token validation logic)
            user_id = self.validate_token(token)
            if not user_id:
                return self.create_error_response(
                    message="Token tidak valid",
                    status_code=401,
                    code="INVALID_TOKEN"
                )
            
            # Add user_id to request context
            request_context["user_id"] = user_id
            
            return handler(request_context)
        
        return wrapper
    
    def admin_required(self, handler: Callable) -> Callable:
        """Decorator untuk routes yang memerlukan role admin"""
        @wraps(handler)
        def wrapper(request_context: Dict[str, Any]) -> Dict[str, Any]:
            # Check if user is authenticated
            if "user_id" not in request_context:
                return self.create_error_response(
                    message="Autentikasi diperlukan",
                    status_code=401,
                    code="AUTHENTICATION_REQUIRED"
                )
            
            # Check user role (implement your role checking logic)
            user_role = self.get_user_role(request_context["user_id"])
            if user_role != "admin":
                return self.create_error_response(
                    message="Akses ditolak. Diperlukan role admin",
                    status_code=403,
                    code="ACCESS_DENIED"
                )
            
            return handler(request_context)
        
        return wrapper
    
    def validate_token(self, token: str) -> Optional[str]:
        """Validate JWT token and return user_id"""
        # TODO: Implement JWT token validation
        # This is a placeholder implementation
        try:
            # Decode JWT token
            # payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            # return payload.get("user_id")
            
            # Placeholder: return dummy user_id for testing
            if token == "valid_token":
                return "user_123"
            return None
        except Exception:
            return None
    
    def get_user_role(self, user_id: str) -> Optional[str]:
        """Get user role from database"""
        # TODO: Implement user role retrieval from database
        # This is a placeholder implementation
        if user_id == "admin_123":
            return "admin"
        return "user"
    
    def extract_pagination(self, query_params: Dict[str, str]) -> Dict[str, Any]:
        """Extract pagination parameters from query string"""
        try:
            page = int(query_params.get("page", 1))
            limit = int(query_params.get("limit", 10))
            
            # Validate pagination parameters
            if page < 1:
                page = 1
            if limit < 1 or limit > 100:
                limit = 10
            
            return {
                "page": page,
                "limit": limit
            }
        except ValueError:
            return {
                "page": 1,
                "limit": 10
            }
    
    def extract_search_params(self, query_params: Dict[str, str]) -> Dict[str, Any]:
        """Extract search parameters from query string"""
        search_params = {}
        
        if "q" in query_params:
            search_params["query"] = query_params["q"]
        
        if "sort_by" in query_params:
            search_params["sort_by"] = query_params["sort_by"]
        
        if "sort_order" in query_params:
            search_params["sort_order"] = query_params["sort_order"]
        
        return search_params
    
    def extract_filter_params(self, query_params: Dict[str, str], allowed_filters: list) -> Dict[str, Any]:
        """Extract filter parameters from query string"""
        filter_params = {}
        
        for filter_key in allowed_filters:
            if filter_key in query_params:
                value = query_params[filter_key]
                
                # Handle boolean values
                if value.lower() in ["true", "false"]:
                    filter_params[filter_key] = value.lower() == "true"
                # Handle numeric values
                elif value.isdigit():
                    filter_params[filter_key] = int(value)
                # Handle string values
                else:
                    filter_params[filter_key] = value
        
        return filter_params
    
    def create_success_response(
        self, 
        data: Any = None, 
        message: str = "Success", 
        status_code: int = 200
    ) -> Dict[str, Any]:
        """Create success response"""
        return {
            "success": True,
            "status_code": status_code,
            "message": message,
            "data": data
        }
    
    def create_error_response(
        self, 
        message: str = "Error", 
        status_code: int = 400, 
        code: str = "ERROR",
        details: Any = None
    ) -> Dict[str, Any]:
        """Create error response"""
        response = {
            "success": False,
            "status_code": status_code,
            "message": message,
            "code": code
        }
        
        if details:
            response["details"] = details
        
        return response
    
    def handle_exception(self, exception: Exception) -> Dict[str, Any]:
        """Handle service exceptions"""
        if isinstance(exception, ValidationException):
            return self.create_error_response(
                message=str(exception),
                status_code=400,
                code="VALIDATION_ERROR"
            )
        elif isinstance(exception, NotFoundException):
            return self.create_error_response(
                message=str(exception),
                status_code=404,
                code="NOT_FOUND"
            )
        elif isinstance(exception, PermissionException):
            return self.create_error_response(
                message=str(exception),
                status_code=403,
                code="PERMISSION_DENIED"
            )
        elif isinstance(exception, ServiceException):
            return self.create_error_response(
                message=str(exception),
                status_code=400,
                code="SERVICE_ERROR"
            )
        else:
            # Log unexpected errors
            print(f"Unexpected error: {str(exception)}")
            return self.create_error_response(
                message="Terjadi kesalahan internal server",
                status_code=500,
                code="INTERNAL_SERVER_ERROR"
            )
    
    def generate_request_id(self) -> str:
        """Generate unique request ID"""
        import uuid
        return str(uuid.uuid4())
    
    def log_request(self, request_context: Dict[str, Any], response: Dict[str, Any]) -> None:
        """Log request and response for monitoring"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "method": request_context["method"],
            "path": request_context["path"],
            "status_code": response.get("status_code"),
            "success": response.get("success"),
            "user_id": request_context.get("user_id"),
            "request_id": response.get("request_id")
        }
        
        # TODO: Implement proper logging (file, database, or external service)
        print(f"Request Log: {json.dumps(log_data)}")
    
    def validate_content_type(self, headers: Dict[str, str], expected: str = "application/json") -> bool:
        """Validate request content type"""
        content_type = headers.get("Content-Type", "")
        return content_type.startswith(expected)
    
    def sanitize_input(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize input data"""
        # TODO: Implement input sanitization
        # Remove potentially dangerous characters, validate data types, etc.
        return data
    
    def get_all_routes(self) -> list:
        """
        Get all registered routes for this router
        This method should be overridden by child classes
        """
        return []