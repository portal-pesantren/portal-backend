from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from core.db import db_config
import logging
from dotenv import load_dotenv
import os
from pathlib import Path

# Load environment variables from .env file
env_file = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_file)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Menginisialisasi koneksi database...")
        db_config.connect()
        logger.info("Database berhasil terkoneksi")
    except Exception as e:
        logger.error(f"Gagal menginisialisasi database: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    try:
        logger.info("Menutup koneksi database...")
        db_config.close_connection()
        logger.info("Koneksi database ditutup")
    except Exception as e:
        logger.error(f"Error saat menutup database: {str(e)}")

def create_app():
    # Import router inside function to avoid circular import
    from routers.pesantren_router import pesantren_router
    from routers.news_router import news_router
    from routers.review_router import review_router
    from routers.user_fastapi_router import user_router
    from routers.application_fastapi_router import application_router
    from routers.consultation_fastapi_router import consultation_router
    
    app = FastAPI(
        title="Portal Pesantren API",
        description="API for Portal Pesantren Application",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Create main router
    main_router = APIRouter()
    
    # Health check endpoint
    @main_router.get("/health")
    async def health_check():
        return {"status": "healthy", "message": "Portal Pesantren API is running"}
    
    # API info endpoint
    @main_router.get("/")
    async def api_info():
        return {
            "name": "Portal Pesantren API",
            "version": "1.0.0",
            "description": "API for Portal Pesantren Application"
        }
    
    # Include main router
    app.include_router(main_router)
    app.include_router(pesantren_router, prefix="/api/v1", tags=["Pesantren"])    
    app.include_router(user_router, prefix="/api/v1", tags=["Users"])   
    app.include_router(review_router, prefix="/api/v1", tags=["Reviews"])
    app.include_router(application_router, prefix="/api/v1", tags=["Applications"])   
    app.include_router(news_router, prefix="/api/v1", tags=["News"])
    app.include_router(consultation_router, prefix="/api/v1", tags=["Consultations"])

    return app