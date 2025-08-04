from typing import Dict, Any, List
from .base_router import BaseRouter
from .user_router import UserRouter
from .review_router import ReviewRouter
from .application_router import ApplicationRouter
from .news_router import NewsRouter
from .consultation_router import ConsultationRouter

class AppRouter(BaseRouter):
    """Main application router yang mengintegrasikan semua router domain"""
    
    def __init__(self):
        super().__init__()
        self.domain_routers = {}
        self._initialize_routers()
        self._register_routes()
    
    def _initialize_routers(self):
        """Initialize semua domain routers"""
        self.domain_routers = {
            "user": UserRouter(),
            "review": ReviewRouter(),
            "application": ApplicationRouter(),
            "news": NewsRouter(),
            "consultation": ConsultationRouter()
        }
        # Note: pesantren router now uses FastAPI APIRouter instead of class-based router
    
    def _register_routes(self):
        """Register routes dari semua domain routers"""
        
        # Health check endpoint
        @self.get("/health")
        def health_check(request_context: Dict[str, Any]) -> Dict[str, Any]:
            return self.create_success_response(
                data={
                    "status": "healthy",
                    "service": "Portal Pesantren API",
                    "version": "1.0.0",
                    "timestamp": self._get_current_timestamp()
                },
                message="Service is running properly"
            )
        
        # API info endpoint
        @self.get("/")
        def api_info(request_context: Dict[str, Any]) -> Dict[str, Any]:
            return self.create_success_response(
                data={
                    "name": "Portal Pesantren API",
                    "version": "1.0.0",
                    "description": "API untuk Portal Pesantren - Platform pencarian dan informasi pesantren",
                    "endpoints": {
                        "health": "/health",
                        "docs": "/docs",
                        "pesantren": "/api/v1/pesantren",
                        "users": "/api/v1/users",
                        "reviews": "/api/v1/reviews",
                        "applications": "/api/v1/applications",
                        "news": "/api/v1/news",
                        "consultations": "/api/v1/consultations"
                    },
                    "timestamp": self._get_current_timestamp()
                },
                message="Welcome to Portal Pesantren API"
            )
        
        # API documentation endpoint
        @self.get("/docs")
        def api_docs(request_context: Dict[str, Any]) -> Dict[str, Any]:
            return self.create_success_response(
                data={
                    "title": "Portal Pesantren API Documentation",
                    "version": "1.0.0",
                    "base_url": "/api/v1",
                    "authentication": {
                        "type": "Bearer Token",
                        "header": "Authorization",
                        "format": "Bearer <token>"
                    },
                    "endpoints": self._get_api_endpoints(),
                    "response_format": {
                        "success": {
                            "success": True,
                            "message": "string",
                            "data": "object",
                            "timestamp": "string"
                        },
                        "error": {
                            "success": False,
                            "message": "string",
                            "error": "object",
                            "timestamp": "string"
                        },
                        "paginated": {
                            "success": True,
                            "message": "string",
                            "data": "array",
                            "pagination": {
                                "page": "number",
                                "limit": "number",
                                "total": "number",
                                "total_pages": "number",
                                "has_next": "boolean",
                                "has_prev": "boolean"
                            },
                            "timestamp": "string"
                        }
                    }
                },
                message="API documentation retrieved successfully"
            )
    
    def _get_api_endpoints(self) -> Dict[str, Any]:
        """Get all API endpoints documentation"""
        return {
            "pesantren": {
                "base_path": "/api/v1/pesantren",
                "endpoints": [
                    "GET /pesantren - Get all pesantren",
                    "GET /pesantren/featured - Get featured pesantren",
                    "GET /pesantren/popular - Get popular pesantren",
                    "GET /pesantren/stats - Get pesantren statistics",
                    "GET /pesantren/{id} - Get pesantren by ID",
                    "POST /pesantren - Create new pesantren",
                    "PUT /pesantren/{id} - Update pesantren",
                    "PATCH /pesantren/{id}/featured - Set featured status",
                    "DELETE /pesantren/{id} - Delete pesantren"
                ]
            },
            "users": {
                "base_path": "/api/v1/users",
                "endpoints": [
                    "POST /users/register - User registration",
                    "POST /users/login - User login",
                    "POST /users/verify-email - Verify email",
                    "POST /users/reset-password - Reset password",
                    "GET /users/profile - Get user profile",
                    "PUT /users/profile - Update user profile",
                    "PATCH /users/change-password - Change password",
                    "GET /users - Get all users (admin)",
                    "GET /users/stats - Get user statistics (admin)",
                    "GET /users/{id} - Get user by ID (admin)",
                    "PATCH /users/{id}/deactivate - Deactivate user (admin)",
                    "PATCH /users/{id}/activate - Activate user (admin)"
                ]
            },
            "reviews": {
                "base_path": "/api/v1/reviews",
                "endpoints": [
                    "GET /reviews - Get all reviews",
                    "GET /reviews/pesantren/{id} - Get reviews by pesantren",
                    "GET /reviews/user/{id} - Get reviews by user",
                    "GET /reviews/stats - Get review statistics",
                    "GET /reviews/{id} - Get review by ID",
                    "POST /reviews - Create new review",
                    "PUT /reviews/{id} - Update review",
                    "POST /reviews/{id}/helpful - Mark review as helpful",
                    "POST /reviews/{id}/report - Report review",
                    "PATCH /reviews/{id}/moderate - Moderate review (admin)",
                    "DELETE /reviews/{id} - Delete review"
                ]
            },
            "applications": {
                "base_path": "/api/v1/applications",
                "endpoints": [
                    "GET /applications - Get all applications",
                    "GET /applications/pesantren/{id} - Get applications by pesantren",
                    "GET /applications/user/{id} - Get applications by user",
                    "GET /applications/stats - Get application statistics",
                    "GET /applications/{id} - Get application by ID",
                    "POST /applications - Create new application",
                    "PUT /applications/{id} - Update application",
                    "PATCH /applications/{id}/status - Update application status",
                    "PATCH /applications/{id}/interview - Schedule interview",
                    "POST /applications/{id}/documents - Upload documents",
                    "PATCH /applications/{id}/cancel - Cancel application"
                ]
            },
            "news": {
                "base_path": "/api/v1/news",
                "endpoints": [
                    "GET /news - Get all news",
                    "GET /news/featured - Get featured news",
                    "GET /news/popular - Get popular news",
                    "GET /news/stats - Get news statistics",
                    "GET /news/slug/{slug} - Get news by slug",
                    "GET /news/{id} - Get news by ID",
                    "GET /news/{id}/related - Get related news",
                    "POST /news - Create new news",
                    "PUT /news/{id} - Update news",
                    "PATCH /news/{id}/publish - Publish news",
                    "PATCH /news/{id}/unpublish - Unpublish news",
                    "POST /news/{id}/like - Like news",
                    "POST /news/{id}/dislike - Dislike news",
                    "DELETE /news/{id}/like - Remove like",
                    "DELETE /news/{id}/dislike - Remove dislike",
                    "DELETE /news/{id} - Delete news"
                ]
            },
            "consultations": {
                "base_path": "/api/v1/consultations",
                "endpoints": [
                    "GET /consultations - Get all consultations",
                    "GET /consultations/stats - Get consultation statistics",
                    "GET /consultations/analytics - Get consultation analytics",
                    "GET /consultations/{id} - Get consultation by ID",
                    "POST /consultations - Create new consultation",
                    "PUT /consultations/{id} - Update consultation",
                    "POST /consultations/{id}/responses - Create consultation response",
                    "PATCH /consultations/{id}/assign - Assign consultant",
                    "PATCH /consultations/{id}/status - Update consultation status",
                    "POST /consultations/{id}/rating - Rate consultation",
                    "DELETE /consultations/{id} - Delete consultation"
                ]
            }
        }
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat() + "Z"
    
    def get_domain_router(self, domain: str) -> BaseRouter:
        """Get specific domain router"""
        return self.domain_routers.get(domain)
    
    def get_all_routes(self) -> Dict[str, Any]:
        """Get all routes from all domain routers"""
        all_routes = {}
        
        # Add main app routes
        all_routes.update(self.routes)
        
        # Add domain routes with prefix
        for domain, router in self.domain_routers.items():
            domain_routes = router.get_routes()
            for path, route_info in domain_routes.items():
                # Add API version prefix
                prefixed_path = f"/api/v1{path}"
                all_routes[prefixed_path] = route_info
        
        return all_routes
    
    def handle_request(self, method: str, path: str, request_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming HTTP request"""
        try:
            # Check if it's a main app route
            if path in self.routes:
                route_info = self.routes[path]
                if method.upper() in route_info["methods"]:
                    handler = route_info["methods"][method.upper()]
                    return handler(request_context)
            
            # Check domain routes
            if path.startswith("/api/v1/"):
                # Remove API prefix
                domain_path = path[7:]  # Remove "/api/v1"
                
                # Find matching domain
                for domain, router in self.domain_routers.items():
                    if domain_path.startswith(f"/{domain}"):
                        # Remove domain prefix
                        route_path = domain_path[len(f"/{domain}"):] or "/"
                        
                        # Handle request in domain router
                        domain_routes = router.get_routes()
                        if route_path in domain_routes:
                            route_info = domain_routes[route_path]
                            if method.upper() in route_info["methods"]:
                                handler = route_info["methods"][method.upper()]
                                return handler(request_context)
            
            # Route not found
            return self.create_error_response(
                message="Endpoint tidak ditemukan",
                status_code=404,
                code="ROUTE_NOT_FOUND",
                error={"path": path, "method": method}
            )
            
        except Exception as e:
            return self.handle_exception(e)
    
    def get_routes(self) -> Dict[str, Any]:
        """Get all registered routes"""
        return self.get_all_routes()