from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import os
from typing import Optional
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """
    Konfigurasi database MongoDB untuk Portal Pesantren
    """
    
    def __init__(self):
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
        self.database_name = os.getenv('DATABASE_NAME', 'portal_pesantren')
        self.client: Optional[MongoClient] = None
        self.database: Optional[Database] = None
        
    def connect(self) -> Database:
        """
        Membuat koneksi ke MongoDB
        """
        try:
            self.client = MongoClient(self.mongo_uri)
            self.database = self.client[self.database_name]
            
            # Test koneksi
            self.client.admin.command('ping')
            logger.info(f"MongoDB Connected: {self.database_name}")
            
            # Setup indexes
            self._setup_indexes()
            
            return self.database
            
        except Exception as e:
            logger.error(f"Gagal terhubung ke MongoDB: {str(e)}")
            raise
    
    def _setup_indexes(self):
        """
        Setup indexes untuk optimasi query
        """
        try:
            # Indexes untuk collection pesantren
            pesantren_collection = self.database['pesantren']
            pesantren_collection.create_index([('name', 'text'), ('description', 'text')])
            pesantren_collection.create_index('location')
            pesantren_collection.create_index('rating')
            pesantren_collection.create_index('featured')
            pesantren_collection.create_index('status')
            
            # Indexes untuk collection users
            users_collection = self.database['users']
            users_collection.create_index('email', unique=True)
            users_collection.create_index('phone')
            users_collection.create_index('role')
            
            # Indexes untuk collection reviews
            reviews_collection = self.database['reviews']
            reviews_collection.create_index('pesantren_id')
            reviews_collection.create_index('user_id')
            reviews_collection.create_index('rating')
            reviews_collection.create_index('created_at')
            
            # Indexes untuk collection applications
            applications_collection = self.database['applications']
            applications_collection.create_index('pesantren_id')
            applications_collection.create_index('user_id')
            applications_collection.create_index('status')
            applications_collection.create_index('created_at')
            
            logger.info("Indexes berhasil dibuat")
            
        except Exception as e:
            logger.error(f"Create Index Failed: {str(e)}")
    
    def get_collection(self, collection_name: str) -> Collection:
        """
        Mendapatkan collection dari database
        """
        if self.database is None:
            raise Exception("Database belum terkoneksi")
        return self.database[collection_name]
    
    def close_connection(self):
        """
        Menutup koneksi database
        """
        if self.client:
            self.client.close()
            logger.info("Koneksi database ditutup")

# Instance global database
db_config = DatabaseConfig()

def get_database() -> Database:
    """
    Mendapatkan instance database
    """
    if db_config.database is None:
        return db_config.connect()
    return db_config.database

def get_collection(collection_name: str) -> Collection:
    """
    Mendapatkan collection dari database
    """
    database = get_database()
    return database[collection_name]

# Collections yang tersedia
COLLECTIONS = {
    'pesantren': 'pesantren',
    'users': 'users',
    'reviews': 'reviews',
    'applications': 'applications',
    'news': 'news',
    'consultations': 'consultations',
    'facilities': 'facilities',
    'programs': 'programs'
}