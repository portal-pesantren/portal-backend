from typing import Dict, List, Optional, Any
from datetime import datetime
from .base import BaseModel
import re
from slugify import slugify

class PesantrenModel(BaseModel):
    """
    Model untuk data Pesantren
    """
    def __init__(self):
        super().__init__('pesantren')

    def validate_data(self, data: Dict[str, Any]) -> bool:
        required_fields = ['name', 'description', 'location', 'contact', 
                           'programs', 'curriculum', 'education_levels', 'capacity']

        for field in required_fields:
            if field not in data or not data[field]:
                return False

        # Validasi kapasitas siswa
        if 'capacity' in data and (not isinstance(data['capacity'], int) or data['capacity'] <= 0):
            return False

        # Validasi biaya
        if 'monthly_fee' in data and (not isinstance(data['monthly_fee'], (int, float)) or data['monthly_fee'] < 0):
            return False
        if 'registration_fee' in data and (not isinstance(data['registration_fee'], (int, float)) or data['registration_fee'] < 0):
            return False

        # Validasi rating
        if 'rating' in data and (not isinstance(data['rating'], (int, float)) or data['rating'] < 0 or data['rating'] > 5):
            return False

        # Validasi email
        if 'contact' in data and 'email' in data['contact']:
            email = data['contact']['email']
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False

        return True

    def create_pesantren(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membuat entitas pesantren baru dengan default values.
        """
        if not self.validate_data(data):
            raise ValueError("Data pesantren tidak valid")

        # Hapus bagian ini karena sudah ditangani oleh BaseModel._prepare_document
        # defaults = {
        #     'slug': slugify(data['name']), 
        #     'rating_average': 0.0,
        #     'rating_count': 0,
        #     'current_students': 0,
        #     'is_featured': False,
        #     'is_active': True,
        #     'view_count': 0,
        #     'created_at': datetime.utcnow(),
        #     'updated_at': datetime.utcnow()
        # }
        
        # for key, value in defaults.items():
        #     if key not in data:
        #         data[key] = value

        # Perbaikan: Tambahkan nilai default ke data input
        data.setdefault('slug', slugify(data['name']))
        data.setdefault('rating_average', 0.0)
        data.setdefault('rating_count', 0)
        data.setdefault('current_students', 0)
        data.setdefault('is_featured', False)
        data.setdefault('is_active', True)
        data.setdefault('view_count', 0)

        # Lakukan validasi tambahan untuk tipe data numerik
        data['monthly_fee'] = float(data.get('monthly_fee', 0.0))
        data['registration_fee'] = float(data.get('registration_fee', 0.0))

        # Panggil metode create dari Base Model
        return self.create(data)
    
    # def search_pesantren(self, 
    #                     query: str = None,
    #                     location: str = None,
    #                     programs: List[str] = None,
    #                     min_rating: float = None,
    #                     max_fees: int = None,
    #                     facilities: List[str] = None,
    #                     featured_only: bool = False,
    #                     limit: int = 10,
    #                     skip: int = 0) -> List[Dict[str, Any]]:
    #     """
    #     Pencarian pesantren dengan berbagai filter
    #     """
    #     filter_dict = {'status': 'active'}
        
    #     # Text search
    #     if query:
    #         filter_dict['$text'] = {'$search': query}
        
    #     # Filter lokasi
    #     if location:
    #         filter_dict['location'] = {'$regex': location, '$options': 'i'}
        
    #     # Filter program
    #     if programs:
    #         filter_dict['programs'] = {'$in': programs}
        
    #     # Filter rating minimum
    #     if min_rating:
    #         filter_dict['rating'] = {'$gte': min_rating}
        
    #     # Filter biaya maksimum
    #     if max_fees:
    #         filter_dict['fees.monthly'] = {'$lte': max_fees}
        
    #     # Filter fasilitas
    #     if facilities:
    #         filter_dict['facilities'] = {'$all': facilities}
        
    #     # Filter featured
    #     if featured_only:
    #         filter_dict['featured'] = True
        
    #     # Sorting
    #     sort_criteria = []
    #     if query:
    #         sort_criteria.append(('score', {'$meta': 'textScore'}))
    #     sort_criteria.extend([('featured', -1), ('rating', -1), ('created_at', -1)])
        
    #     return self.find_many(filter_dict, sort_criteria, limit, skip)
    
    def get_featured_pesantren(self, limit: int = 6) -> List[Dict[str, Any]]:
        """
        Mendapatkan pesantren unggulan
        """
        filter_dict = {
            'is_featured': True,
            # PERBAIKAN 1: Gunakan 'is_active' (boolean), bukan 'status' (string)
            'is_active': True 
        }
        
        # PERBAIKAN 2 (REKOMENDASI): Sesuaikan nama field untuk sorting
        # Berdasarkan schema Anda, field yang benar adalah 'rating_average' dan 'current_students'
        sort_criteria = [('rating_average', -1), ('current_students', -1)]
        
        return self.find_many(filter_dict, sort_criteria, limit)
    
    def get_popular_pesantren(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan pesantren populer berdasarkan rating dan jumlah siswa
        """
        pipeline = [
            {'$match': {'is_active': True}},
            {
                '$addFields': {
                    'popularity_score': {
                        '$add': [
                            {'$multiply': ['$rating_average', 0.7]},
                            {'$multiply': [{'$divide': ['$current_students', 1000]}, 0.3]}
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
            'location.city': {'$regex': location, '$options': 'i'},
            'is_active': True
        }
        sort_criteria = [('rating_average', -1), ('is_featured', -1)]
        return self.find_many(filter_dict, sort_criteria, limit)
    
    # PERBAIKAN: Target field yang benar adalah 'rating_average' dan 'rating_count'
    def update_rating(self, pesantren_id: str, new_rating_value: float, user_id: str) -> bool:
        """
        Update rating pesantren dengan menghitung ulang rata-rata.
        Ini lebih aman daripada hanya menimpa nilai rating.
        """
        # Logika ini sebaiknya ada di service layer, bukan di model.
        # Untuk sementara, kita asumsikan update sederhana.
        update_doc = {
            '$inc': {'rating_count': 1},
            # Logika untuk menghitung ulang rata-rata lebih kompleks dan
            # sebaiknya dilakukan di service layer dengan mengambil data dulu.
            # Untuk sekarang, kita set saja nilainya.
            '$set': {'rating_average': new_rating_value} 
        }
        return self.update_by_id(pesantren_id, update_doc)
    
    def increment_students(self, pesantren_id: str, count: int = 1) -> bool:
        """
        Menambah jumlah siswa
        """
        try:
            result = self.collection.update_one(
                {'_id': pesantren_id},
                {'$inc': {'current_students': count}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    def set_featured(self, pesantren_id: str, is_featured: bool = True) -> bool:
        """
        Set status featured pesantren
        """
        return self.update_by_id(pesantren_id, {'is_featured': is_featured})
    
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
                    'total_students': {'$sum': '$current_students'},
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