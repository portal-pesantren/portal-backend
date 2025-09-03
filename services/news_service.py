# services/news_service.py

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from bson import ObjectId
import re
import math 
from models.news import NewsModel
# Asumsi model User dan custom exceptions sudah ada
# from models.user import UserModel 
# from core.exceptions import NotFoundException, ValidationException, PermissionException

# Placeholder
class UserModel:
    def find_by_id(self, user_id):
        return {"id": user_id, "role": "admin"} # Mock user

class NotFoundException(Exception): pass
class ValidationException(Exception): pass
class PermissionException(Exception): pass
class DuplicateException(Exception): pass

from dto.news_dto import (
    NewsCreateDTO, NewsUpdateDTO, NewsResponseDTO, NewsSummaryDTO, 
    NewsSearchDTO, NewsFilterDTO, NewsStatsDTO, NewsLikeDTO,
    NewsPublishDTO, NewsFeatureDTO
)
from dto.base_dto import PaginationDTO, PaginatedResponseDTO, SuccessResponseDTO

class NewsService:
    """Service untuk mengelola logika bisnis berita"""
    
    def __init__(self):
        self.model = NewsModel()
        self.user_model = UserModel() # Ganti dengan UserModel yang sebenarnya
        
    def _generate_slug(self, title: str, doc_id_to_exclude: Optional[str] = None) -> str:
        """Generate URL-friendly slug unik dari title."""
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug).strip()
        slug = re.sub(r'[\s-]+', '-', slug)
        
        base_slug = slug
        counter = 1
        
        while True:
            query = {"slug": slug}
            if doc_id_to_exclude:
                query["_id"] = {"$ne": ObjectId(doc_id_to_exclude)}
                
            if not self.model.find_one(query):
                break
            slug = f"{base_slug}-{counter}"
            counter += 1
            
        return slug

    def _generate_excerpt(self, content: str, max_length: int = 160) -> str:
        """Generate excerpt dari content."""
        clean_content = re.sub(r'<[^>]+>', '', content)
        if len(clean_content) <= max_length:
            return clean_content
        excerpt = clean_content[:max_length].rsplit(' ', 1)[0]
        return excerpt + "..."
    
    def _calculate_reading_time(self, content: str) -> int:
        """Hitung estimasi waktu baca (menit)."""
        clean_content = re.sub(r'<[^>]+>', '', content)
        word_count = len(clean_content.split())
        return max(1, round(word_count / 200))

    def get_news_by_id_or_slug(self, identifier: str, increment_view: bool = True) -> NewsResponseDTO:
        """Mendapatkan satu berita berdasarkan ID atau slug-nya."""
        is_object_id = ObjectId.is_valid(identifier)
        if is_object_id:
            news = self.model.find_with_details(identifier)
        else:
            news_base = self.model.find_one({"slug": identifier, "status": "published"})
            if not news_base:
                raise NotFoundException(f"Berita dengan slug '{identifier}' tidak ditemukan.")
            news = self.model.find_with_details(news_base['id'])

        if not news:
            raise NotFoundException(f"Berita dengan identifier '{identifier}' tidak ditemukan.")
        
        if increment_view and news.get("is_published"):
            self.model.increment_views(news['id'])
            news['views'] = news.get('views', 0) + 1
            
        return NewsResponseDTO.model_validate(news)

    def get_news_list(
        self,
        page: int,
        limit: int,
        search_dto: NewsSearchDTO,
        filter_dto: NewsFilterDTO
    ) -> PaginatedResponseDTO[NewsSummaryDTO]:
        """Mendapatkan daftar berita dengan filter, search, dan pagination."""
        query = {}
        query['status'] = {'$ne': 'deleted'}
        
        # Filtering
        if filter_dto.is_published is not None:
             query['status'] = 'published' if filter_dto.is_published else 'draft'
        
        # Hapus 'deleted' news dari hasil
        query['status'] = {'$ne': 'deleted'}
        
        if filter_dto.category: query['category'] = filter_dto.category
        if filter_dto.pesantren_id: query['pesantren_id'] = filter_dto.pesantren_id
        if filter_dto.author_id: query['author_id'] = filter_dto.author_id
        if filter_dto.is_featured is not None: query['is_featured'] = filter_dto.is_featured
        
        # Searching
        if search_dto.query:
            query['$text'] = {'$search': search_dto.query} # Gunakan text search MongoDB
        
        # Sorting
        sort_map = {
            "date": "publish_date",
            "views": "views",
            "likes": "likes",
            "title": "title"
        }
        sort_field = sort_map.get(search_dto.sort_by, "publish_date")
        sort_order = -1 if search_dto.sort_order == 'desc' else 1
        sort = [(sort_field, sort_order)]
        
        skip = (page - 1) * limit
        news_list = self.model.find_many(query, sort, limit, skip)
        total = self.model.count(query)
        
        total_pages = math.ceil(total / limit) if total > 0 else 1
        
        pagination_details = PaginationDTO(
            page=page,
            limit=limit,
            total=total,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1
        )
        
        data = [NewsSummaryDTO.model_validate(news) for news in news_list]
        
        return PaginatedResponseDTO(
            data=data,
            pagination=pagination_details
        )

    def create_news(self, news_data: NewsCreateDTO, author_id: str) -> NewsResponseDTO:
        """Membuat berita baru."""
        # Siapkan data untuk model
        data_to_create = news_data.model_dump()
        data_to_create['author_id'] = author_id
        data_to_create['slug'] = self._generate_slug(news_data.title)
        
        if not news_data.excerpt:
            data_to_create['excerpt'] = self._generate_excerpt(news_data.content)
            
        data_to_create['reading_time'] = self._calculate_reading_time(news_data.content)
        
        # Jika ada publish_date, berarti 'published'. Jika tidak, 'draft'.
        if news_data.publish_date:
            data_to_create['status'] = 'published'
        else:
            data_to_create['status'] = 'draft'
            data_to_create.pop('publish_date', None) # Hapus jika None
            
        new_news = self.model.create_news(data_to_create)
        
        # Ambil data lengkap dengan info author
        full_news = self.model.find_with_details(new_news['id'])
        return NewsResponseDTO.model_validate(full_news)

    def update_news(self, news_id: str, news_data: NewsUpdateDTO, user_id: str) -> NewsResponseDTO:
        """Update berita."""
        existing_news = self.model.find_by_id(news_id)
        if not existing_news:
            raise NotFoundException(f"Berita dengan ID '{news_id}' tidak ditemukan.")
            
        # TODO: Implement permission check (e.g., only author or admin can update)
        
        update_payload = news_data.model_dump(exclude_unset=True)
        
        if 'title' in update_payload:
            update_payload['slug'] = self._generate_slug(update_payload['title'], doc_id_to_exclude=news_id)
            
        if 'content' in update_payload:
            update_payload['reading_time'] = self._calculate_reading_time(update_payload['content'])
            if 'excerpt' not in update_payload:
                update_payload['excerpt'] = self._generate_excerpt(update_payload['content'])

        if 'is_published' in update_payload:
             status = 'published' if update_payload['is_published'] else 'draft'
             update_payload['status'] = status
             if status == 'published' and not existing_news.get('publish_date'):
                 update_payload['publish_date'] = datetime.now(timezone.utc)
             elif status == 'draft':
                 update_payload['publish_date'] = None
             del update_payload['is_published']

        updated_news = self.model.update_news(news_id, update_payload)
        if not updated_news:
             raise Exception("Gagal mengupdate berita di database.")

        full_news = self.model.find_with_details(updated_news['id'])
        return NewsResponseDTO.model_validate(full_news)
    
    def feature_news(self, news_id: str, feature_data: NewsFeatureDTO, user_id: str) -> NewsResponseDTO:
        """
        Mengubah status 'is_featured' pada sebuah berita.
        Lebih efisien karena hanya mengupdate satu field.
        """
        # 1. Cek apakah berita ada
        if not self.model.find_by_id(news_id):
            raise NotFoundException(f"Berita dengan ID '{news_id}' tidak ditemukan.")
        
        # TODO: Implementasi pengecekan izin (misal: hanya admin/editor yang bisa)
        # user = self.user_model.find_by_id(user_id)
        # if user['role'] not in ['admin', 'editor']:
        #     raise PermissionException("Anda tidak memiliki izin untuk melakukan aksi ini.")
            
        # 2. Siapkan payload untuk update
        update_payload = {"is_featured": feature_data.is_featured}
        
        # 3. Panggil metode update di model
        updated_news = self.model.update_news(news_id, update_payload)
        if not updated_news:
             raise Exception("Gagal mengubah status unggulan berita di database.")

        # 4. Ambil data lengkap (dengan join author, dll) untuk response
        full_news = self.model.find_with_details(updated_news['id'])
        if not full_news:
            # Fallback jika find_with_details gagal, meskipun seharusnya tidak
            raise NotFoundException(f"Berita dengan ID '{news_id}' tidak ditemukan setelah diupdate.")
            
        return NewsResponseDTO.model_validate(full_news)


    def delete_news(self, news_id: str, user_id: str):
        """Soft delete berita."""
        if not self.model.find_by_id(news_id):
            raise NotFoundException(f"Berita dengan ID '{news_id}' tidak ditemukan.")
            
        # TODO: Implement permission check
            
        if not self.model.soft_delete_news(news_id):
            raise Exception("Gagal menghapus berita.")
        return {"id": news_id, "status": "deleted"}

    def like_news(self, news_id: str, like_data: NewsLikeDTO, user_id: str):
        """Like, dislike, atau remove like/dislike."""
        if not self.model.find_by_id(news_id):
            raise NotFoundException(f"Berita dengan ID '{news_id}' tidak ditemukan.")
        
        self.model.manage_like(news_id, user_id, like_data.action)
        
        # Ambil data terbaru untuk response
        updated_news = self.model.find_by_id(news_id)
        return {
            "id": news_id,
            "likes": updated_news.get('likes', 0),
            "dislikes": updated_news.get('dislikes', 0)
        }