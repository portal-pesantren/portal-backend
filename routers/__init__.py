# Routers Layer
from .base_router import BaseRouter
from .user_router import UserRouter
# from .review_router import ReviewRouter  # Converted to FastAPI APIRouter
from .application_router import ApplicationRouter
# from .news_router import NewsRouter  # Converted to FastAPI APIRouter
from .consultation_router import ConsultationRouter
from .app_router import AppRouter

# FastAPI Routers
from .pesantren_router import pesantren_router
from .user_fastapi_router import user_router
from .review_router import review_router
from .application_fastapi_router import application_router
from .news_router import news_router
from .consultation_fastapi_router import consultation_router

__all__ = [
    "BaseRouter",
    "UserRouter",
    # "ReviewRouter",  # Converted to FastAPI APIRouter
    "ApplicationRouter",
    # "NewsRouter",  # Converted to FastAPI APIRouter
    "ConsultationRouter",
    "AppRouter",
    "pesantren_router",
    "user_router",
    "review_router",
    "application_router",
    "news_router",
    "consultation_router"
]