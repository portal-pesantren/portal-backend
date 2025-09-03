# models/news.py

from typing import Dict, List, Optional, Any
from .base import BaseModel # Menggunakan base_model.py yang Anda berikan
from datetime import datetime, timezone
from bson import ObjectId
import re

class NewsModel(BaseModel):
    """
    Model untuk data News/Article.
    Fokus pada interaksi dengan database secara efisien dan aman.
    """
    
    def __init__(self):
        super().__init__('news')

    def validate_data(self, data: Dict[str, Any]) -> bool:
        # Metode ini tidak lagi diperlukan karena validasi penuh dilakukan oleh DTO di service layer.
        # Cukup return True untuk memenuhi syarat abstract method.
        return True
    
    def create_news(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membuat dokumen berita baru di database.
        Data diasumsikan sudah divalidasi dan disiapkan oleh Service.
        """
        # Menambahkan field default yang dikontrol oleh model
        data['status'] = data.get('status', 'draft') # 'draft', 'published', 'deleted'
        data['views'] = 0
        data['likes'] = 0
        data['dislikes'] = 0
        data['liked_by'] = []
        data['disliked_by'] = []
        
        return self.create(data)

    def update_news(self, news_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update berita berdasarkan ID. Mengembalikan dokumen yang sudah diupdate.
        """
        return self.find_one_and_update({'_id': ObjectId(news_id)}, data)

    def soft_delete_news(self, news_id: str) -> bool:
        """
        Melakukan soft delete pada berita.
        """
        update_data = {
            'status': 'deleted',
            'deleted_at': datetime.now(timezone.utc)
        }
        return self.update_by_id(news_id, update_data)

    def increment_views(self, news_id: str) -> bool:
        """
        Increment view count secara atomik menggunakan $inc.
        Ini lebih aman dari race condition daripada read-modify-write.
        """
        result = self.collection.update_one(
            {'_id': ObjectId(news_id)},
            {'$inc': {'views': 1}}
        )
        return result.modified_count > 0

    def manage_like(self, news_id: str, user_id: str, action: str) -> bool:
        """
        Mengelola like/dislike secara atomik menggunakan $addToSet dan $pull.
        """
        oid_news_id = ObjectId(news_id)
        
        if action == 'like':
            # Tambahkan user ke 'liked_by', hapus dari 'disliked_by' jika ada
            # $addToSet memastikan user_id tidak duplikat
            update_pipeline = {
                '$addToSet': {'liked_by': user_id},
                '$pull': {'disliked_by': user_id}
            }
        elif action == 'dislike':
            # Tambahkan user ke 'disliked_by', hapus dari 'liked_by' jika ada
            update_pipeline = {
                '$addToSet': {'disliked_by': user_id},
                '$pull': {'liked_by': user_id}
            }
        elif action == 'remove':
            # Hapus user dari kedua list
            update_pipeline = {
                '$pull': {'liked_by': user_id, 'disliked_by': user_id}
            }
        else:
            return False

        # Lakukan update
        result = self.collection.update_one({'_id': oid_news_id}, update_pipeline)
        
        # Setelah mengubah list, update count berdasarkan ukuran array
        # Ini bisa dilakukan dengan aggregation pipeline update (lebih kompleks)
        # atau dengan read-after-write yang cukup aman di sini.
        news = self.find_by_id(news_id)
        if news:
            like_count = len(news.get('liked_by', []))
            dislike_count = len(news.get('disliked_by', []))
            self.update_by_id(news_id, {'likes': like_count, 'dislikes': dislike_count})
        
        return result.modified_count > 0

    def find_with_details(self, news_id: str) -> Optional[Dict[str, Any]]:
        """
        Mencari berita dan menggabungkan dengan data author/pesantren (jika diperlukan).
        Menggunakan aggregation pipeline.
        """
        pipeline = [
            {'$match': {'_id': ObjectId(news_id)}},
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'author_id',
                    'foreignField': '_id', # Asumsi ID user juga ObjectId
                    'as': 'author_info'
                }
            },
            {
                '$lookup': {
                    'from': 'pesantren',
                    'localField': 'pesantren_id',
                    'foreignField': '_id', # Asumsi ID pesantren juga ObjectId
                    'as': 'pesantren_info'
                }
            },
            {
                '$unwind': {
                    'path': '$author_info',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$unwind': {
                    'path': '$pesantren_info',
                    'preserveNullAndEmptyArrays': True
                }
            },
            {
                '$addFields': {
                    'author_name': '$author_info.name',
                    'author_avatar': '$author_info.avatar',
                    'pesantren_name': '$pesantren_info.name',
                    'is_published': {'$eq': ['$status', 'published']}
                }
            },
            {
                '$project': {
                    'author_info': 0,
                    'pesantren_info': 0,
                    'liked_by': 0,      # Jangan ekspos list user yang like/dislike
                    'disliked_by': 0
                }
            }
        ]
        result = self.aggregate(pipeline)
        return result[0] if result else None