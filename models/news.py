from typing import Dict, List, Optional, Any
from .base import BaseModel
from datetime import datetime, timedelta
import re

class NewsModel(BaseModel):
    """
    Model untuk data News/Article
    """
    
    def __init__(self):
        super().__init__('news')
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validasi data news
        """
        required_fields = ['title', 'content', 'author_id', 'category']
        
        # Cek field yang wajib ada
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        # Validasi title tidak kosong
        if not data['title'].strip():
            return False
        
        # Validasi content tidak kosong
        if not data['content'].strip():
            return False
        
        # Validasi category
        valid_categories = [
            'berita', 'artikel', 'tips', 'panduan', 'event', 
            'pengumuman', 'prestasi', 'kegiatan'
        ]
        if data['category'] not in valid_categories:
            return False
        
        return True
    
    def create_news(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membuat news baru dengan validasi
        """
        if not self.validate_data(data):
            raise ValueError("Data news tidak valid")
        
        # Generate slug dari title (sudah termasuk pengecekan keunikan)
        slug = self._generate_slug(data['title'])
        
        # Set default values
        defaults = {
            'slug': slug,
            'excerpt': data.get('excerpt', self._generate_excerpt(data['content'])),
            'featured_image': data.get('featured_image', ''),
            'status': 'draft',
            'published_date': None,
            'view_count': 0,
            'like_count': 0,
            'comment_count': 0,
            'tags': data.get('tags', []),
            'meta_title': data.get('meta_title', data['title']),
            'meta_description': data.get('meta_description', ''),
            'reading_time': self._calculate_reading_time(data['content']),
            'featured': False,
            'allow_comments': True,
            'pesantren_id': data.get('pesantren_id', None)  # Untuk news spesifik pesantren
        }
        
        # Merge dengan default values
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return self.create(data)
    
    def _generate_base_slug(self, title: str) -> str:
        """
        Generate base slug dari title tanpa pengecekan keunikan
        """
        # Lowercase dan replace spasi dengan dash
        slug = title.lower()
        # Hapus karakter khusus
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        # Replace spasi dengan dash
        slug = re.sub(r'\s+', '-', slug)
        # Hapus dash berlebihan
        slug = re.sub(r'-+', '-', slug)
        # Hapus dash di awal dan akhir
        slug = slug.strip('-')
        
        return slug
    
    def _generate_slug(self, title: str) -> str:
        """
        Generate slug dari title dengan pengecekan keunikan
        """
        base_slug = self._generate_base_slug(title)
        
        # Cek keunikan slug dan tambahkan counter jika perlu
        slug = base_slug
        counter = 1
        while self.find_one({"slug": slug}):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        return slug
    
    def _generate_excerpt(self, content: str, max_length: int = 200) -> str:
        """
        Generate excerpt dari content
        """
        # Hapus HTML tags jika ada
        clean_content = re.sub(r'<[^>]+>', '', content)
        
        if len(clean_content) <= max_length:
            return clean_content
        
        # Potong di kata terakhir yang lengkap
        excerpt = clean_content[:max_length]
        last_space = excerpt.rfind(' ')
        if last_space > 0:
            excerpt = excerpt[:last_space]
        
        return excerpt + '...'
    
    def _calculate_reading_time(self, content: str) -> int:
        """
        Hitung estimasi waktu baca (dalam menit)
        """
        # Hapus HTML tags
        clean_content = re.sub(r'<[^>]+>', '', content)
        # Hitung kata (asumsi 200 kata per menit)
        word_count = len(clean_content.split())
        reading_time = max(1, round(word_count / 200))
        
        return reading_time
    
    def publish_news(self, news_id: str, published_by: str) -> bool:
        """
        Publish news
        """
        update_data = {
            'status': 'published',
            'published_date': datetime.utcnow(),
            'published_by': published_by,
            'updated_at': datetime.utcnow()
        }
        
        return self.update_by_id(news_id, update_data)
    
    def unpublish_news(self, news_id: str) -> bool:
        """
        Unpublish news (kembali ke draft)
        """
        update_data = {
            'status': 'draft',
            'published_date': None,
            'updated_at': datetime.utcnow()
        }
        
        return self.update_by_id(news_id, update_data)
    
    def get_published_news(self, category: str = None, featured: bool = None,
                          limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan news yang sudah dipublish
        """
        filter_dict = {'status': 'published'}
        
        if category:
            filter_dict['category'] = category
        
        if featured is not None:
            filter_dict['is_featured'] = featured
        
        return self.find_many(filter_dict, [('published_date', -1)], limit, skip)
    
    def get_news_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan news berdasarkan slug
        """
        return self.find_one({'slug': slug, 'status': 'published'})
    
    def get_news_by_author(self, author_id: str, status: str = None,
                          limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan news berdasarkan author
        """
        filter_dict = {'author_id': author_id}
        
        if status:
            filter_dict['status'] = status
        
        return self.find_many(filter_dict, [('created_at', -1)], limit, skip)
    
    def get_news_by_pesantren(self, pesantren_id: str, limit: int = 10, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan news berdasarkan pesantren
        """
        filter_dict = {
            'pesantren_id': pesantren_id,
            'status': 'published'
        }
        
        return self.find_many(filter_dict, [('published_date', -1)], limit, skip)
    
    def increment_view_count(self, news_id: str) -> bool:
        """
        Increment view count
        """
        news = self.find_by_id(news_id)
        if not news:
            return False
        
        current_count = news.get('view_count', 0)
        return self.update_by_id(news_id, {'view_count': current_count + 1})
    
    def like_news(self, news_id: str, user_id: str) -> bool:
        """
        Like news
        """
        news = self.find_by_id(news_id)
        if not news:
            return False
        
        liked_users = news.get('liked_users', [])
        if user_id in liked_users:
            return False  # Sudah pernah like
        
        liked_users.append(user_id)
        
        return self.update_by_id(news_id, {
            'liked_users': liked_users,
            'like_count': len(liked_users)
        })
    
    def unlike_news(self, news_id: str, user_id: str) -> bool:
        """
        Unlike news
        """
        news = self.find_by_id(news_id)
        if not news:
            return False
        
        liked_users = news.get('liked_users', [])
        if user_id not in liked_users:
            return False  # Belum pernah like
        
        liked_users.remove(user_id)
        
        return self.update_by_id(news_id, {
            'liked_users': liked_users,
            'like_count': len(liked_users)
        })
    
    def set_featured(self, news_id: str, featured: bool = True) -> bool:
        """
        Set/unset news sebagai featured
        """
        return self.update_by_id(news_id, {
            'featured': featured,
            'updated_at': datetime.utcnow()
        })
    
    def update_news(self, news_id: str, data: Dict[str, Any], updated_by: str) -> bool:
        """
        Update news
        """
        # Field yang boleh diupdate
        allowed_fields = [
            'title', 'content', 'excerpt', 'category', 'tags',
            'featured_image', 'meta_title', 'meta_description',
            'allow_comments'
        ]
        
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return False
        
        # Update slug jika title berubah
        if 'title' in update_data:
            # Generate slug baru dengan pengecekan keunikan (exclude current news)
            base_slug = self._generate_base_slug(update_data['title'])
            new_slug = base_slug
            counter = 1
            while True:
                existing_news = self.find_one({
                    'slug': new_slug,
                    'id': {'$ne': news_id}
                })
                if not existing_news:
                    break
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            update_data['slug'] = new_slug
        
        # Update reading time jika content berubah
        if 'content' in update_data:
            update_data['reading_time'] = self._calculate_reading_time(update_data['content'])
        
        # Update excerpt jika content berubah dan excerpt tidak disediakan
        if 'content' in update_data and 'excerpt' not in update_data:
            update_data['excerpt'] = self._generate_excerpt(update_data['content'])
        
        update_data['updated_by'] = updated_by
        update_data['updated_at'] = datetime.utcnow()
        
        return self.update_by_id(news_id, update_data)
    
    def search_news(self, query: Dict[str, Any] = None, skip: int = 0, 
                   limit: int = 20, sort: List[tuple] = None) -> List[Dict[str, Any]]:
        """
        Pencarian news berdasarkan query dict dengan pagination dan sorting
        """
        if query is None:
            query = {}
        
        # Default sort jika tidak ada
        if sort is None:
            sort = [('published_at', -1)]
        
        return self.find_many(query, sort, limit, skip)
    
    def count_documents(self, query: Dict[str, Any] = None) -> int:
        """
        Menghitung jumlah dokumen berdasarkan query
        """
        if query is None:
            query = {}
        return self.count(query)
    
    def search_news_by_text(self, query: str, category: str = None, tags: List[str] = None,
                   limit: int = 20) -> List[Dict[str, Any]]:
        """
        Pencarian news berdasarkan title, content, atau tags (method lama)
        """
        filter_dict = {
            '$or': [
                {'title': {'$regex': query, '$options': 'i'}},
                {'content': {'$regex': query, '$options': 'i'}},
                {'tags': {'$regex': query, '$options': 'i'}}
            ],
            'status': 'published'
        }
        
        if category:
            filter_dict['category'] = category
        
        if tags:
            filter_dict['tags'] = {'$in': tags}
        
        return self.find_many(filter_dict, [('published_at', -1)], limit)
    
    def get_popular_news(self, days: int = 30, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan news populer berdasarkan view count
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        filter_dict = {
            'status': 'published',
            'published_date': {'$gte': since_date}
        }
        
        return self.find_many(filter_dict, [('view_count', -1), ('like_count', -1)], limit)
    
    def get_related_news(self, news_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Mendapatkan news terkait berdasarkan category dan tags
        """
        news = self.find_by_id(news_id)
        if not news:
            return []
        
        filter_dict = {
            'id': {'$ne': news_id},
            'status': 'published',
            '$or': [
                {'category': news.get('category')},
                {'tags': {'$in': news.get('tags', [])}}
            ]
        }
        
        return self.find_many(filter_dict, [('published_date', -1)], limit)
    
    def get_news_statistics(self, author_id: str = None) -> Dict[str, Any]:
        """
        Mendapatkan statistik news
        """
        match_filter = {}
        if author_id:
            match_filter['author_id'] = author_id
        
        pipeline = [
            {'$match': match_filter},
            {
                '$group': {
                    '_id': None,
                    'total_news': {'$sum': 1},
                    'published': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'published']}, 1, 0]}
                    },
                    'draft': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'draft']}, 1, 0]}
                    },
                    'featured': {
                        '$sum': {'$cond': ['$featured', 1, 0]}
                    },
                    'total_views': {'$sum': '$view_count'},
                    'total_likes': {'$sum': '$like_count'},
                    'avg_reading_time': {'$avg': '$reading_time'}
                }
            }
        ]
        
        result = self.aggregate(pipeline)
        return result[0] if result else {}
    
    def get_trending_tags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan tags yang sedang trending
        """
        pipeline = [
            {
                '$match': {
                    'status': 'published',
                    'tags': {'$exists': True, '$ne': []}
                }
            },
            {'$unwind': '$tags'},
            {
                '$group': {
                    '_id': '$tags',
                    'count': {'$sum': 1},
                    'total_views': {'$sum': '$view_count'}
                }
            },
            {'$sort': {'count': -1, 'total_views': -1}},
            {'$limit': limit},
            {
                '$project': {
                    'tag': '$_id',
                    'count': 1,
                    'total_views': 1,
                    '_id': 0
                }
            }
        ]
        
        return self.aggregate(pipeline)
    
    def delete_news(self, news_id: str) -> bool:
        """
        Hapus news (soft delete)
        """
        return self.update_by_id(news_id, {
            'status': 'deleted',
            'deleted_at': datetime.utcnow()
        })