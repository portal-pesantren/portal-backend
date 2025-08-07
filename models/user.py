from typing import Dict, List, Optional, Any
from .base import BaseModel
import re
import hashlib
import secrets
from datetime import datetime, timedelta

class UserModel(BaseModel):
    """
    Model untuk data User
    """
    
    def __init__(self):
        super().__init__('users')
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validasi data user
        """
        required_fields = ['name', 'email', 'role']
        
        # Cek field yang wajib ada
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        # Validasi email
        email = data['email']
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
        
        # Validasi role
        valid_roles = ['parent', 'admin', 'pesantren_admin']
        if data['role'] not in valid_roles:
            return False
        
        # Validasi phone jika ada
        if 'phone' in data and data['phone']:
            phone = data['phone']
            # Bersihkan nomor telepon dari karakter non-digit kecuali +
            clean_phone = re.sub(r'[^+0-9]', '', phone)
            # Format phone Indonesia: +62 atau 08
            phone_pattern = r'^(\+62|62|0)8[1-9][0-9]{6,9}$'
            if not re.match(phone_pattern, clean_phone):
                return False
        
        return True
    
    def _hash_password(self, password: str) -> str:
        """
        Hash password menggunakan SHA256 dengan salt
        """
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verifikasi password
        """
        try:
            salt, password_hash = hashed_password.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == password_hash
        except ValueError:
            return False
    
    def create_user(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membuat user baru dengan validasi
        """
        if not self.validate_data(data):
            raise ValueError("Data user tidak valid")
        
        # Cek apakah email sudah ada
        existing_user = self.find_one({'email': data['email']})
        if existing_user:
            raise ValueError("Email sudah terdaftar")
        
        # Hash password jika ada
        if 'password' in data:
            data['password'] = self._hash_password(data['password'])
        
        # Set default values
        defaults = {
            'avatar': '',
            'is_active': True,
            'is_verified': False,
            'email_verified': False,
            'phone_verified': False,
            'last_login': None,
            'login_count': 0,
            'profile_picture': None,
            'address': None,
            'date_of_birth': None,
            'gender': None,
            'occupation': None,
            'preferences': {
                'notifications': True,
                'newsletter': True
            },
            'profile': {
                'bio': '',
                'location': '',
                'children_count': 0
            }
        }
        
        # Merge dengan default values
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return self.create(data)
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Autentikasi user dengan email dan password
        """
        user = self.find_one({'email': email, 'is_active': True})
        
        if not user:
            return None
            
        if 'password' not in user:
            return None
        
        if self._verify_password(password, user['password']):
            # Update last login
            self.update_by_id(user['id'], {'last_login': datetime.utcnow()})
            
            # Hapus password dari response
            del user['password']
            return user
        
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan user berdasarkan email
        """
        user = self.find_one({'email': email})
        if user and 'password' in user:
            del user['password']  # Jangan return password
        return user
    
    def update_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Update password user
        """
        user = self.find_by_id(user_id)
        if not user or 'password' not in user:
            return False
        
        # Verifikasi password lama
        if not self._verify_password(old_password, user['password']):
            return False
        
        # Hash password baru
        new_hashed_password = self._hash_password(new_password)
        
        return self.update_by_id(user_id, {'password': new_hashed_password})
    
    def reset_password(self, email: str, new_password: str) -> bool:
        """
        Reset password user (untuk forgot password)
        """
        user = self.find_one({'email': email})
        if not user:
            return False
        
        new_hashed_password = self._hash_password(new_password)
        return self.update_by_id(user['id'], {'password': new_hashed_password})
    
    def verify_email(self, user_id: str) -> bool:
        """
        Verifikasi email user
        """
        return self.update_by_id(user_id, {'email_verified': True})
    
    def verify_phone(self, user_id: str) -> bool:
        """
        Verifikasi phone user
        """
        return self.update_by_id(user_id, {'phone_verified': True})
    
    def update_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """
        Update profil user
        """
        allowed_fields = ['name', 'phone', 'avatar', 'profile', 'preferences']
        
        # Filter hanya field yang diizinkan
        update_data = {k: v for k, v in profile_data.items() if k in allowed_fields}
        
        if not update_data:
            return False
        
        return self.update_by_id(user_id, update_data)
    
    def deactivate_user(self, user_id: str) -> bool:
        """
        Nonaktifkan user
        """
        return self.update_by_id(user_id, {'status': 'inactive'})
    
    def activate_user(self, user_id: str) -> bool:
        """
        Aktifkan user
        """
        return self.update_by_id(user_id, {'status': 'active'})
    
    def get_users_by_role(self, role: str, limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan user berdasarkan role
        """
        filter_dict = {'role': role, 'status': 'active'}
        sort_criteria = [('created_at', -1)]
        
        users = self.find_many(filter_dict, sort_criteria, limit, skip)
        
        # Hapus password dari semua user
        for user in users:
            if 'password' in user:
                del user['password']
        
        return users
    
    def search_users(self, query: str, role: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Pencarian user berdasarkan nama atau email
        """
        filter_dict = {
            '$or': [
                {'name': {'$regex': query, '$options': 'i'}},
                {'email': {'$regex': query, '$options': 'i'}}
            ],
            'status': 'active'
        }
        
        if role:
            filter_dict['role'] = role
        
        users = self.find_many(filter_dict, [('name', 1)], limit)
        
        # Hapus password dari semua user
        for user in users:
            if 'password' in user:
                del user['password']
        
        return users
    
    def get_user_statistics(self) -> Dict[str, Any]:
        """
        Mendapatkan statistik user
        """
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_users': {'$sum': 1},
                    'active_users': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'active']}, 1, 0]}
                    },
                    'verified_emails': {
                        '$sum': {'$cond': ['$email_verified', 1, 0]}
                    },
                    'parents': {
                        '$sum': {'$cond': [{'$eq': ['$role', 'parent']}, 1, 0]}
                    },
                    'admins': {
                        '$sum': {'$cond': [{'$eq': ['$role', 'admin']}, 1, 0]}
                    },
                    'pesantren_admins': {
                        '$sum': {'$cond': [{'$eq': ['$role', 'pesantren_admin']}, 1, 0]}
                    }
                }
            }
        ]
        
        result = self.aggregate(pipeline)
        return result[0] if result else {}
    
    def get_recent_users(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan user yang baru mendaftar
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        filter_dict = {
            'created_at': {'$gte': since_date},
            'status': 'active'
        }
        
        users = self.find_many(filter_dict, [('created_at', -1)], limit)
        
        # Hapus password dari semua user
        for user in users:
            if 'password' in user:
                del user['password']
        
        return users