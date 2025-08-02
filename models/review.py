from typing import Dict, List, Optional, Any
from .base import BaseModel
from datetime import datetime, timedelta

class ReviewModel(BaseModel):
    """
    Model untuk data Review pesantren
    """
    
    def __init__(self):
        super().__init__('reviews')
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validasi data review
        """
        required_fields = ['pesantren_id', 'user_id', 'rating', 'comment']
        
        # Cek field yang wajib ada
        for field in required_fields:
            if field not in data or data[field] is None:
                return False
        
        # Validasi rating (1-5)
        rating = data['rating']
        if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
            return False
        
        # Validasi comment tidak kosong
        if not data['comment'].strip():
            return False
        
        return True
    
    def create_review(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membuat review baru dengan validasi
        """
        if not self.validate_data(data):
            raise ValueError("Data review tidak valid")
        
        # Cek apakah user sudah pernah review pesantren ini
        existing_review = self.find_one({
            'pesantren_id': data['pesantren_id'],
            'user_id': data['user_id']
        })
        
        if existing_review:
            raise ValueError("User sudah pernah memberikan review untuk pesantren ini")
        
        # Set default values
        defaults = {
            'status': 'active',
            'helpful_count': 0,
            'reported_count': 0,
            'aspects': {
                'fasilitas': data.get('aspects', {}).get('fasilitas', 0),
                'pengajaran': data.get('aspects', {}).get('pengajaran', 0),
                'lingkungan': data.get('aspects', {}).get('lingkungan', 0),
                'biaya': data.get('aspects', {}).get('biaya', 0)
            },
            'photos': data.get('photos', []),
            'verified': False
        }
        
        # Merge dengan default values
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return self.create(data)
    
    def get_reviews_by_pesantren(self, pesantren_id: str, limit: int = 20, skip: int = 0, 
                                sort_by: str = 'created_at') -> List[Dict[str, Any]]:
        """
        Mendapatkan review berdasarkan pesantren
        """
        filter_dict = {
            'pesantren_id': pesantren_id,
            'status': 'active'
        }
        
        # Sorting options
        sort_options = {
            'created_at': [('created_at', -1)],
            'rating_high': [('rating', -1), ('created_at', -1)],
            'rating_low': [('rating', 1), ('created_at', -1)],
            'helpful': [('helpful_count', -1), ('created_at', -1)]
        }
        
        sort_criteria = sort_options.get(sort_by, [('created_at', -1)])
        
        return self.find_many(filter_dict, sort_criteria, limit, skip)
    
    def get_reviews_by_user(self, user_id: str, limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan review berdasarkan user
        """
        filter_dict = {
            'user_id': user_id,
            'status': 'active'
        }
        
        return self.find_many(filter_dict, [('created_at', -1)], limit, skip)
    
    def get_review_statistics(self, pesantren_id: str) -> Dict[str, Any]:
        """
        Mendapatkan statistik review untuk pesantren
        """
        pipeline = [
            {
                '$match': {
                    'pesantren_id': pesantren_id,
                    'status': 'active'
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_reviews': {'$sum': 1},
                    'average_rating': {'$avg': '$rating'},
                    'rating_1': {
                        '$sum': {'$cond': [{'$eq': ['$rating', 1]}, 1, 0]}
                    },
                    'rating_2': {
                        '$sum': {'$cond': [{'$eq': ['$rating', 2]}, 1, 0]}
                    },
                    'rating_3': {
                        '$sum': {'$cond': [{'$eq': ['$rating', 3]}, 1, 0]}
                    },
                    'rating_4': {
                        '$sum': {'$cond': [{'$eq': ['$rating', 4]}, 1, 0]}
                    },
                    'rating_5': {
                        '$sum': {'$cond': [{'$eq': ['$rating', 5]}, 1, 0]}
                    },
                    'avg_fasilitas': {'$avg': '$aspects.fasilitas'},
                    'avg_pengajaran': {'$avg': '$aspects.pengajaran'},
                    'avg_lingkungan': {'$avg': '$aspects.lingkungan'},
                    'avg_biaya': {'$avg': '$aspects.biaya'}
                }
            }
        ]
        
        result = self.aggregate(pipeline)
        if result:
            stats = result[0]
            # Bulatkan average rating
            if stats.get('average_rating'):
                stats['average_rating'] = round(stats['average_rating'], 1)
            return stats
        
        return {
            'total_reviews': 0,
            'average_rating': 0,
            'rating_1': 0, 'rating_2': 0, 'rating_3': 0, 'rating_4': 0, 'rating_5': 0,
            'avg_fasilitas': 0, 'avg_pengajaran': 0, 'avg_lingkungan': 0, 'avg_biaya': 0
        }
    
    def update_review(self, review_id: str, user_id: str, data: Dict[str, Any]) -> bool:
        """
        Update review (hanya oleh pemilik review)
        """
        # Cek apakah review milik user
        review = self.find_one({'id': review_id, 'user_id': user_id})
        if not review:
            return False
        
        # Field yang boleh diupdate
        allowed_fields = ['rating', 'comment', 'aspects', 'photos']
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return False
        
        # Validasi rating jika ada
        if 'rating' in update_data:
            rating = update_data['rating']
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return False
        
        # Set updated_at
        update_data['updated_at'] = datetime.utcnow()
        
        return self.update_by_id(review_id, update_data)
    
    def mark_helpful(self, review_id: str, user_id: str) -> bool:
        """
        Tandai review sebagai helpful
        """
        # Cek apakah user sudah pernah mark helpful
        review = self.find_by_id(review_id)
        if not review:
            return False
        
        helpful_users = review.get('helpful_users', [])
        if user_id in helpful_users:
            return False  # Sudah pernah mark helpful
        
        # Tambah user ke helpful_users dan increment helpful_count
        helpful_users.append(user_id)
        
        return self.update_by_id(review_id, {
            'helpful_users': helpful_users,
            'helpful_count': len(helpful_users)
        })
    
    def unmark_helpful(self, review_id: str, user_id: str) -> bool:
        """
        Hapus mark helpful dari review
        """
        review = self.find_by_id(review_id)
        if not review:
            return False
        
        helpful_users = review.get('helpful_users', [])
        if user_id not in helpful_users:
            return False  # Belum pernah mark helpful
        
        # Hapus user dari helpful_users dan decrement helpful_count
        helpful_users.remove(user_id)
        
        return self.update_by_id(review_id, {
            'helpful_users': helpful_users,
            'helpful_count': len(helpful_users)
        })
    
    def report_review(self, review_id: str, user_id: str, reason: str) -> bool:
        """
        Laporkan review
        """
        review = self.find_by_id(review_id)
        if not review:
            return False
        
        # Cek apakah user sudah pernah report
        reported_users = review.get('reported_users', [])
        if user_id in reported_users:
            return False  # Sudah pernah report
        
        # Tambah user ke reported_users dan increment reported_count
        reported_users.append(user_id)
        reports = review.get('reports', [])
        reports.append({
            'user_id': user_id,
            'reason': reason,
            'reported_at': datetime.utcnow()
        })
        
        return self.update_by_id(review_id, {
            'reported_users': reported_users,
            'reported_count': len(reported_users),
            'reports': reports
        })
    
    def moderate_review(self, review_id: str, action: str, moderator_id: str) -> bool:
        """
        Moderasi review (approve/reject/hide)
        """
        valid_actions = ['approve', 'reject', 'hide']
        if action not in valid_actions:
            return False
        
        status_map = {
            'approve': 'active',
            'reject': 'rejected',
            'hide': 'hidden'
        }
        
        update_data = {
            'status': status_map[action],
            'moderated_by': moderator_id,
            'moderated_at': datetime.utcnow()
        }
        
        return self.update_by_id(review_id, update_data)
    
    def verify_review(self, review_id: str) -> bool:
        """
        Verifikasi review (untuk review dari user terverifikasi)
        """
        return self.update_by_id(review_id, {
            'verified': True,
            'verified_at': datetime.utcnow()
        })
    
    def delete_review(self, review_id: str, user_id: str) -> bool:
        """
        Hapus review (soft delete)
        """
        # Cek apakah review milik user
        review = self.find_one({'id': review_id, 'user_id': user_id})
        if not review:
            return False
        
        return self.update_by_id(review_id, {
            'status': 'deleted',
            'deleted_at': datetime.utcnow()
        })
    
    def get_recent_reviews(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan review terbaru
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        filter_dict = {
            'created_at': {'$gte': since_date},
            'status': 'active'
        }
        
        return self.find_many(filter_dict, [('created_at', -1)], limit)
    
    def get_top_reviews(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan review dengan rating tertinggi dan paling helpful
        """
        filter_dict = {
            'status': 'active',
            'rating': {'$gte': 4},
            'helpful_count': {'$gte': 1}
        }
        
        sort_criteria = [('rating', -1), ('helpful_count', -1), ('created_at', -1)]
        
        return self.find_many(filter_dict, sort_criteria, limit)
    
    def search_reviews(self, query: str, pesantren_id: str = None, 
                      min_rating: int = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Pencarian review berdasarkan komentar
        """
        filter_dict = {
            'comment': {'$regex': query, '$options': 'i'},
            'status': 'active'
        }
        
        if pesantren_id:
            filter_dict['pesantren_id'] = pesantren_id
        
        if min_rating:
            filter_dict['rating'] = {'$gte': min_rating}
        
        return self.find_many(filter_dict, [('created_at', -1)], limit)