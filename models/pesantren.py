from typing import Dict, List, Optional, Any
from .base import BaseModel
import re

class PesantrenModel(BaseModel):
    """
    Model untuk data Pesantren
    """
    
    def __init__(self):
        super().__init__('pesantren')
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validasi data pesantren
        """
        required_fields = ['name', 'location', 'address', 'description']
        
        # Cek field yang wajib ada
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        # Validasi rating (1-5)
        if 'rating' in data:
            rating = data['rating']
            if not isinstance(rating, (int, float)) or rating < 1 or rating > 5:
                return False
        
        # Validasi students (harus positif)
        if 'students' in data:
            students = data['students']
            if not isinstance(students, int) or students < 0:
                return False
        
        # Validasi email jika ada
        if 'contact' in data and 'email' in data['contact']:
            email = data['contact']['email']
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False
        
        return True
    
    def create_pesantren(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membuat pesantren baru dengan validasi
        """
        if not self.validate_data(data):
            raise ValueError("Data pesantren tidak valid")
        
        # Set default values
        defaults = {
            'rating': 0.0,
            'students': 0,
            'programs': [],
            'facilities': [],
            'featured': False,
            'status': 'active',
            'image': '',
            'fees': {
                'monthly': 0,
                'registration': 0,
                'other': 0
            },
            'contact': {
                'phone': '',
                'email': '',
                'website': ''
            }
        }
        
        # Merge dengan default values
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return self.create(data)
    
    def search_pesantren(self, 
                        query: str = None,
                        location: str = None,
                        programs: List[str] = None,
                        min_rating: float = None,
                        max_fees: int = None,
                        facilities: List[str] = None,
                        featured_only: bool = False,
                        limit: int = 10,
                        skip: int = 0) -> List[Dict[str, Any]]:
        """
        Pencarian pesantren dengan berbagai filter
        """
        filter_dict = {'status': 'active'}
        
        # Text search
        if query:
            filter_dict['$text'] = {'$search': query}
        
        # Filter lokasi
        if location:
            filter_dict['location'] = {'$regex': location, '$options': 'i'}
        
        # Filter program
        if programs:
            filter_dict['programs'] = {'$in': programs}
        
        # Filter rating minimum
        if min_rating:
            filter_dict['rating'] = {'$gte': min_rating}
        
        # Filter biaya maksimum
        if max_fees:
            filter_dict['fees.monthly'] = {'$lte': max_fees}
        
        # Filter fasilitas
        if facilities:
            filter_dict['facilities'] = {'$all': facilities}
        
        # Filter featured
        if featured_only:
            filter_dict['featured'] = True
        
        # Sorting
        sort_criteria = []
        if query:
            sort_criteria.append(('score', {'$meta': 'textScore'}))
        sort_criteria.extend([('featured', -1), ('rating', -1), ('created_at', -1)])
        
        return self.find_many(filter_dict, sort_criteria, limit, skip)
    
    def get_featured_pesantren(self, limit: int = 6) -> List[Dict[str, Any]]:
        """
        Mendapatkan pesantren unggulan
        """
        filter_dict = {
            'featured': True,
            'status': 'active'
        }
        sort_criteria = [('rating', -1), ('students', -1)]
        
        return self.find_many(filter_dict, sort_criteria, limit)
    
    def get_popular_pesantren(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan pesantren populer berdasarkan rating dan jumlah siswa
        """
        pipeline = [
            {'$match': {'status': 'active'}},
            {
                '$addFields': {
                    'popularity_score': {
                        '$add': [
                            {'$multiply': ['$rating', 0.7]},
                            {'$multiply': [{'$divide': ['$students', 1000]}, 0.3]}
                        ]
                    }
                }
            },
            {'$sort': {'popularity_score': -1}},
            {'$limit': limit}
        ]
        
        return self.aggregate(pipeline)
    
    def get_pesantren_by_location(self, location: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan pesantren berdasarkan lokasi
        """
        filter_dict = {
            'location': {'$regex': location, '$options': 'i'},
            'status': 'active'
        }
        sort_criteria = [('rating', -1), ('featured', -1)]
        
        return self.find_many(filter_dict, sort_criteria, limit)
    
    def update_rating(self, pesantren_id: str, new_rating: float) -> bool:
        """
        Update rating pesantren
        """
        if new_rating < 1 or new_rating > 5:
            return False
        
        return self.update_by_id(pesantren_id, {'rating': new_rating})
    
    def increment_students(self, pesantren_id: str, count: int = 1) -> bool:
        """
        Menambah jumlah siswa
        """
        try:
            result = self.collection.update_one(
                {'_id': pesantren_id},
                {'$inc': {'students': count}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def set_featured(self, pesantren_id: str, featured: bool = True) -> bool:
        """
        Set status featured pesantren
        """
        return self.update_by_id(pesantren_id, {'featured': featured})
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Mendapatkan statistik pesantren
        """
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_pesantren': {'$sum': 1},
                    'active_pesantren': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'active']}, 1, 0]}
                    },
                    'featured_pesantren': {
                        '$sum': {'$cond': ['$featured', 1, 0]}
                    },
                    'total_students': {'$sum': '$students'},
                    'avg_rating': {'$avg': '$rating'},
                    'avg_monthly_fee': {'$avg': '$fees.monthly'}
                }
            }
        ]
        
        result = self.aggregate(pipeline)
        return result[0] if result else {}
    
    def get_locations(self) -> List[str]:
        """
        Mendapatkan daftar lokasi pesantren yang tersedia
        """
        pipeline = [
            {'$match': {'status': 'active'}},
            {'$group': {'_id': '$location'}},
            {'$sort': {'_id': 1}}
        ]
        
        result = self.aggregate(pipeline)
        return [item['_id'] for item in result if item['_id']]
    
    def get_programs(self) -> List[str]:
        """
        Mendapatkan daftar program yang tersedia
        """
        pipeline = [
            {'$match': {'status': 'active'}},
            {'$unwind': '$programs'},
            {'$group': {'_id': '$programs'}},
            {'$sort': {'_id': 1}}
        ]
        
        result = self.aggregate(pipeline)
        return [item['_id'] for item in result if item['_id']]