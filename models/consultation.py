from typing import Dict, List, Optional, Any
from .base import BaseModel
from datetime import datetime, timedelta
import re

class ConsultationModel(BaseModel):
    """
    Model untuk data Consultation
    """
    
    def __init__(self):
        super().__init__('consultations')
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validasi data consultation
        """
        required_fields = ['user_id', 'subject', 'message', 'consultation_type']
        
        # Cek field yang wajib ada
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        # Validasi consultation_type
        valid_types = [
            'general', 'admission', 'curriculum', 'facilities',
            'fees', 'programs', 'location', 'other'
        ]
        if data['consultation_type'] not in valid_types:
            return False
        
        # Validasi subject tidak kosong
        if not data['subject'].strip():
            return False
        
        # Validasi message tidak kosong
        if not data['message'].strip():
            return False
        
        return True
    
    def create_consultation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membuat consultation baru dengan validasi
        """
        if not self.validate_data(data):
            raise ValueError("Data consultation tidak valid")
        
        # Generate ticket number
        ticket_number = self._generate_ticket_number()
        
        # Set default values
        defaults = {
            'ticket_number': ticket_number,
            'status': 'open',
            'priority': 'normal',
            'assigned_to': None,
            'pesantren_id': data.get('pesantren_id', None),
            'contact_method': data.get('contact_method', 'email'),
            'contact_value': data.get('contact_value', ''),
            'preferred_time': data.get('preferred_time', ''),
            'is_urgent': data.get('is_urgent', False),
            'tags': data.get('tags', []),
            'attachments': data.get('attachments', []),
            'response_count': 0,
            'last_response_date': None,
            'resolved_date': None,
            'satisfaction_rating': None,
            'satisfaction_feedback': ''
        }
        
        # Merge dengan default values
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return self.create(data)
    
    def _generate_ticket_number(self) -> str:
        """
        Generate nomor tiket unik
        """
        year = datetime.now().year
        month = datetime.now().month
        
        # Hitung jumlah konsultasi bulan ini
        start_of_month = datetime(year, month, 1)
        if month == 12:
            end_of_month = datetime(year + 1, 1, 1)
        else:
            end_of_month = datetime(year, month + 1, 1)
        
        count = self.count({
            'created_at': {
                '$gte': start_of_month,
                '$lt': end_of_month
            }
        })
        
        # Format: CS-YYYY-MM-XXXX
        return f"CS-{year}-{month:02d}-{count + 1:04d}"
    
    def add_response(self, consultation_id: str, response_data: Dict[str, Any]) -> bool:
        """
        Menambahkan response ke consultation
        """
        required_fields = ['responder_id', 'responder_type', 'message']
        
        # Validasi response data
        for field in required_fields:
            if field not in response_data or not response_data[field]:
                return False
        
        # Validasi responder_type
        if response_data['responder_type'] not in ['user', 'admin', 'pesantren_admin']:
            return False
        
        consultation = self.find_by_id(consultation_id)
        if not consultation:
            return False
        
        # Buat response object
        response = {
            'id': self._generate_id(),
            'responder_id': response_data['responder_id'],
            'responder_type': response_data['responder_type'],
            'message': response_data['message'],
            'attachments': response_data.get('attachments', []),
            'created_at': datetime.utcnow(),
            'is_internal': response_data.get('is_internal', False)
        }
        
        # Tambahkan response ke consultation
        responses = consultation.get('responses', [])
        responses.append(response)
        
        # Update consultation
        update_data = {
            'responses': responses,
            'response_count': len(responses),
            'last_response_date': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        # Jika response dari admin, update status jika masih open
        if (response_data['responder_type'] in ['admin', 'pesantren_admin'] and 
            consultation['status'] == 'open'):
            update_data['status'] = 'in_progress'
        
        return self.update_by_id(consultation_id, update_data)
    
    def update_status(self, consultation_id: str, status: str, updated_by: str,
                     notes: str = '') -> bool:
        """
        Update status consultation
        """
        valid_statuses = ['open', 'in_progress', 'waiting_response', 'resolved', 'closed']
        
        if status not in valid_statuses:
            return False
        
        update_data = {
            'status': status,
            'updated_by': updated_by,
            'updated_at': datetime.utcnow()
        }
        
        if notes:
            update_data['status_notes'] = notes
        
        # Set tanggal resolved jika status resolved
        if status == 'resolved':
            update_data['resolved_date'] = datetime.utcnow()
        
        return self.update_by_id(consultation_id, update_data)
    
    def assign_consultation(self, consultation_id: str, assigned_to: str,
                          assigned_by: str) -> bool:
        """
        Assign consultation ke admin
        """
        update_data = {
            'assigned_to': assigned_to,
            'assigned_by': assigned_by,
            'assigned_date': datetime.utcnow(),
            'status': 'in_progress',
            'updated_at': datetime.utcnow()
        }
        
        return self.update_by_id(consultation_id, update_data)
    
    def set_priority(self, consultation_id: str, priority: str) -> bool:
        """
        Set prioritas consultation
        """
        valid_priorities = ['low', 'normal', 'high', 'urgent']
        
        if priority not in valid_priorities:
            return False
        
        return self.update_by_id(consultation_id, {
            'priority': priority,
            'updated_at': datetime.utcnow()
        })
    
    def add_satisfaction_rating(self, consultation_id: str, user_id: str,
                              rating: int, feedback: str = '') -> bool:
        """
        Menambahkan rating kepuasan
        """
        # Validasi rating (1-5)
        if not isinstance(rating, int) or rating < 1 or rating > 5:
            return False
        
        # Cek apakah consultation milik user
        consultation = self.find_one({
            'id': consultation_id,
            'user_id': user_id,
            'status': {'$in': ['resolved', 'closed']}
        })
        
        if not consultation:
            return False
        
        return self.update_by_id(consultation_id, {
            'satisfaction_rating': rating,
            'satisfaction_feedback': feedback,
            'rated_at': datetime.utcnow()
        })
    
    def get_consultations_by_user(self, user_id: str, status: str = None,
                                limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan consultation berdasarkan user
        """
        filter_dict = {'user_id': user_id}
        
        if status:
            filter_dict['status'] = status
        
        return self.find_many(filter_dict, [('created_at', -1)], limit, skip)
    
    def get_consultations_by_pesantren(self, pesantren_id: str, status: str = None,
                                     limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan consultation berdasarkan pesantren
        """
        filter_dict = {'pesantren_id': pesantren_id}
        
        if status:
            filter_dict['status'] = status
        
        return self.find_many(filter_dict, [('created_at', -1)], limit, skip)
    
    def get_assigned_consultations(self, admin_id: str, status: str = None,
                                 limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan consultation yang di-assign ke admin
        """
        filter_dict = {'assigned_to': admin_id}
        
        if status:
            filter_dict['status'] = status
        
        return self.find_many(filter_dict, [('created_at', -1)], limit, skip)
    
    def get_consultations_by_status(self, status: str, priority: str = None,
                                  limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan consultation berdasarkan status
        """
        filter_dict = {'status': status}
        
        if priority:
            filter_dict['priority'] = priority
        
        # Urutkan berdasarkan prioritas dan tanggal
        sort_criteria = [
            ('priority', -1),  # urgent, high, normal, low
            ('created_at', 1)   # yang lama dulu
        ]
        
        return self.find_many(filter_dict, sort_criteria, limit, skip)
    
    def get_consultation_by_ticket(self, ticket_number: str) -> Optional[Dict[str, Any]]:
        """
        Mendapatkan consultation berdasarkan ticket number
        """
        return self.find_one({'ticket_number': ticket_number})
    
    def search_consultations(self, query: str, status: str = None,
                           consultation_type: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Pencarian consultation berdasarkan subject, message, atau ticket number
        """
        filter_dict = {
            '$or': [
                {'subject': {'$regex': query, '$options': 'i'}},
                {'message': {'$regex': query, '$options': 'i'}},
                {'ticket_number': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        if status:
            filter_dict['status'] = status
        
        if consultation_type:
            filter_dict['consultation_type'] = consultation_type
        
        return self.find_many(filter_dict, [('created_at', -1)], limit)
    
    def get_consultation_statistics(self, pesantren_id: str = None,
                                  admin_id: str = None) -> Dict[str, Any]:
        """
        Mendapatkan statistik consultation
        """
        match_filter = {}
        
        if pesantren_id:
            match_filter['pesantren_id'] = pesantren_id
        
        if admin_id:
            match_filter['assigned_to'] = admin_id
        
        pipeline = [
            {'$match': match_filter},
            {
                '$group': {
                    '_id': None,
                    'total_consultations': {'$sum': 1},
                    'open': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'open']}, 1, 0]}
                    },
                    'in_progress': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'in_progress']}, 1, 0]}
                    },
                    'resolved': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'resolved']}, 1, 0]}
                    },
                    'closed': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'closed']}, 1, 0]}
                    },
                    'urgent_priority': {
                        '$sum': {'$cond': [{'$eq': ['$priority', 'urgent']}, 1, 0]}
                    },
                    'high_priority': {
                        '$sum': {'$cond': [{'$eq': ['$priority', 'high']}, 1, 0]}
                    },
                    'avg_satisfaction': {
                        '$avg': {
                            '$cond': [
                                {'$ne': ['$satisfaction_rating', None]},
                                '$satisfaction_rating',
                                None
                            ]
                        }
                    },
                    'avg_response_count': {'$avg': '$response_count'}
                }
            }
        ]
        
        result = self.aggregate(pipeline)
        return result[0] if result else {}
    
    def get_overdue_consultations(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Mendapatkan consultation yang belum direspon dalam waktu tertentu
        """
        overdue_date = datetime.utcnow() - timedelta(hours=hours)
        
        filter_dict = {
            'status': {'$in': ['open', 'in_progress']},
            '$or': [
                {
                    'last_response_date': None,
                    'created_at': {'$lt': overdue_date}
                },
                {
                    'last_response_date': {'$lt': overdue_date}
                }
            ]
        }
        
        return self.find_many(filter_dict, [('created_at', 1)])
    
    def get_consultation_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Mendapatkan trend consultation dalam periode tertentu
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                '$match': {
                    'created_at': {'$gte': since_date}
                }
            },
            {
                '$group': {
                    '_id': {
                        'date': {
                            '$dateToString': {
                                'format': '%Y-%m-%d',
                                'date': '$created_at'
                            }
                        },
                        'type': '$consultation_type'
                    },
                    'count': {'$sum': 1}
                }
            },
            {
                '$group': {
                    '_id': '$_id.date',
                    'types': {
                        '$push': {
                            'type': '$_id.type',
                            'count': '$count'
                        }
                    },
                    'total': {'$sum': '$count'}
                }
            },
            {'$sort': {'_id': 1}}
        ]
        
        return self.aggregate(pipeline)
    
    def close_consultation(self, consultation_id: str, closed_by: str,
                         reason: str = '') -> bool:
        """
        Tutup consultation
        """
        update_data = {
            'status': 'closed',
            'closed_by': closed_by,
            'closed_date': datetime.utcnow(),
            'close_reason': reason,
            'updated_at': datetime.utcnow()
        }
        
        return self.update_by_id(consultation_id, update_data)