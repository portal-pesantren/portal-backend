from typing import Dict, List, Optional, Any
from .base import BaseModel
from datetime import datetime, timedelta
import re

class ApplicationModel(BaseModel):
    """
    Model untuk data Application (Pendaftaran)
    """
    
    def __init__(self):
        super().__init__('applications')
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validasi data application
        """
        required_fields = [
            'pesantren_id', 'parent_id', 'student_name', 'student_birth_date',
            'student_gender', 'parent_name', 'parent_phone', 'parent_email',
            'address', 'program_id'
        ]
        
        # Cek field yang wajib ada
        for field in required_fields:
            if field not in data or not data[field]:
                return False
        
        # Validasi gender
        if data['student_gender'] not in ['L', 'P']:
            return False
        
        # Validasi email
        email = data['parent_email']
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False
        
        # Validasi phone
        phone = data['parent_phone']
        phone_pattern = r'^(\+62|62|0)8[1-9][0-9]{6,9}$'
        if not re.match(phone_pattern, phone):
            return False
        
        # Validasi birth_date (harus tanggal yang valid)
        try:
            if isinstance(data['student_birth_date'], str):
                datetime.strptime(data['student_birth_date'], '%Y-%m-%d')
        except ValueError:
            return False
        
        return True
    
    def create_application(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membuat application baru dengan validasi
        """
        if not self.validate_data(data):
            raise ValueError("Data application tidak valid")
        
        # Generate application number
        application_number = self._generate_application_number()
        
        # Set default values
        defaults = {
            'application_number': application_number,
            'status': 'pending',
            'submission_date': datetime.utcnow(),
            'documents': {
                'birth_certificate': data.get('documents', {}).get('birth_certificate', ''),
                'family_card': data.get('documents', {}).get('family_card', ''),
                'photo': data.get('documents', {}).get('photo', ''),
                'health_certificate': data.get('documents', {}).get('health_certificate', ''),
                'previous_school_certificate': data.get('documents', {}).get('previous_school_certificate', '')
            },
            'notes': '',
            'interview_date': None,
            'interview_notes': '',
            'payment_status': 'pending',
            'payment_amount': 0,
            'payment_due_date': None,
            'academic_year': self._get_current_academic_year(),
            'priority': 'normal',
            'source': data.get('source', 'website')
        }
        
        # Merge dengan default values
        for key, value in defaults.items():
            if key not in data:
                data[key] = value
        
        return self.create(data)
    
    def _generate_application_number(self) -> str:
        """
        Generate nomor pendaftaran unik
        """
        year = datetime.now().year
        month = datetime.now().month
        
        # Hitung jumlah aplikasi bulan ini
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
        
        # Format: PP-YYYY-MM-XXXX
        return f"PP-{year}-{month:02d}-{count + 1:04d}"
    
    def _get_current_academic_year(self) -> str:
        """
        Mendapatkan tahun akademik saat ini
        """
        now = datetime.now()
        if now.month >= 7:  # Juli - Desember
            return f"{now.year}/{now.year + 1}"
        else:  # Januari - Juni
            return f"{now.year - 1}/{now.year}"
    
    def get_applications_by_pesantren(self, pesantren_id: str, status: str = None,
                                    limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan aplikasi berdasarkan pesantren
        """
        filter_dict = {'pesantren_id': pesantren_id}
        
        if status:
            filter_dict['status'] = status
        
        return self.find_many(filter_dict, [('created_at', -1)], limit, skip)
    
    def get_applications_by_parent(self, parent_id: str, limit: int = 20, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan aplikasi berdasarkan parent
        """
        filter_dict = {'parent_id': parent_id}
        
        return self.find_many(filter_dict, [('created_at', -1)], limit, skip)
    
    def update_application_status(self, application_id: str, status: str, 
                                notes: str = '', updated_by: str = '') -> bool:
        """
        Update status aplikasi
        """
        valid_statuses = [
            'pending', 'reviewed', 'interview_scheduled', 'interviewed',
            'accepted', 'rejected', 'waitlisted', 'enrolled', 'cancelled'
        ]
        
        if status not in valid_statuses:
            return False
        
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if notes:
            update_data['notes'] = notes
        
        if updated_by:
            update_data['updated_by'] = updated_by
        
        # Set tanggal khusus berdasarkan status
        if status == 'accepted':
            update_data['accepted_date'] = datetime.utcnow()
        elif status == 'rejected':
            update_data['rejected_date'] = datetime.utcnow()
        elif status == 'enrolled':
            update_data['enrolled_date'] = datetime.utcnow()
        
        return self.update_by_id(application_id, update_data)
    
    def schedule_interview(self, application_id: str, interview_date: datetime,
                          interview_location: str = '', notes: str = '') -> bool:
        """
        Jadwalkan interview
        """
        update_data = {
            'status': 'interview_scheduled',
            'interview_date': interview_date,
            'interview_location': interview_location,
            'interview_notes': notes,
            'updated_at': datetime.utcnow()
        }
        
        return self.update_by_id(application_id, update_data)
    
    def complete_interview(self, application_id: str, interview_result: str,
                          interview_score: int = None, notes: str = '') -> bool:
        """
        Selesaikan interview
        """
        update_data = {
            'status': 'interviewed',
            'interview_result': interview_result,
            'interview_completed_date': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        if interview_score is not None:
            update_data['interview_score'] = interview_score
        
        if notes:
            update_data['interview_notes'] = notes
        
        return self.update_by_id(application_id, update_data)
    
    def update_payment_status(self, application_id: str, payment_status: str,
                            payment_amount: float = None, payment_date: datetime = None) -> bool:
        """
        Update status pembayaran
        """
        valid_payment_statuses = ['pending', 'partial', 'paid', 'overdue', 'cancelled']
        
        if payment_status not in valid_payment_statuses:
            return False
        
        update_data = {
            'payment_status': payment_status,
            'updated_at': datetime.utcnow()
        }
        
        if payment_amount is not None:
            update_data['payment_amount'] = payment_amount
        
        if payment_date:
            update_data['payment_date'] = payment_date
        elif payment_status == 'paid':
            update_data['payment_date'] = datetime.utcnow()
        
        return self.update_by_id(application_id, update_data)
    
    def upload_document(self, application_id: str, document_type: str, file_path: str) -> bool:
        """
        Upload dokumen aplikasi
        """
        valid_document_types = [
            'birth_certificate', 'family_card', 'photo', 'health_certificate',
            'previous_school_certificate', 'additional_documents'
        ]
        
        if document_type not in valid_document_types:
            return False
        
        application = self.find_by_id(application_id)
        if not application:
            return False
        
        documents = application.get('documents', {})
        documents[document_type] = file_path
        
        return self.update_by_id(application_id, {
            'documents': documents,
            'updated_at': datetime.utcnow()
        })
    
    def get_application_statistics(self, pesantren_id: str = None, 
                                 academic_year: str = None) -> Dict[str, Any]:
        """
        Mendapatkan statistik aplikasi
        """
        match_filter = {}
        
        if pesantren_id:
            match_filter['pesantren_id'] = pesantren_id
        
        if academic_year:
            match_filter['academic_year'] = academic_year
        
        pipeline = [
            {'$match': match_filter},
            {
                '$group': {
                    '_id': None,
                    'total_applications': {'$sum': 1},
                    'pending': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'pending']}, 1, 0]}
                    },
                    'reviewed': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'reviewed']}, 1, 0]}
                    },
                    'accepted': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'accepted']}, 1, 0]}
                    },
                    'rejected': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'rejected']}, 1, 0]}
                    },
                    'enrolled': {
                        '$sum': {'$cond': [{'$eq': ['$status', 'enrolled']}, 1, 0]}
                    },
                    'male_students': {
                        '$sum': {'$cond': [{'$eq': ['$student_gender', 'L']}, 1, 0]}
                    },
                    'female_students': {
                        '$sum': {'$cond': [{'$eq': ['$student_gender', 'P']}, 1, 0]}
                    },
                    'paid_applications': {
                        '$sum': {'$cond': [{'$eq': ['$payment_status', 'paid']}, 1, 0]}
                    }
                }
            }
        ]
        
        result = self.aggregate(pipeline)
        return result[0] if result else {}
    
    def get_applications_by_status(self, status: str, pesantren_id: str = None,
                                 limit: int = 50, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Mendapatkan aplikasi berdasarkan status
        """
        filter_dict = {'status': status}
        
        if pesantren_id:
            filter_dict['pesantren_id'] = pesantren_id
        
        return self.find_many(filter_dict, [('created_at', -1)], limit, skip)
    
    def get_overdue_payments(self, days_overdue: int = 7) -> List[Dict[str, Any]]:
        """
        Mendapatkan aplikasi dengan pembayaran terlambat
        """
        overdue_date = datetime.utcnow() - timedelta(days=days_overdue)
        
        filter_dict = {
            'payment_status': 'pending',
            'payment_due_date': {'$lt': overdue_date},
            'status': {'$in': ['accepted', 'enrolled']}
        }
        
        return self.find_many(filter_dict, [('payment_due_date', 1)])
    
    def search_applications(self, query: str, pesantren_id: str = None,
                          status: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Pencarian aplikasi berdasarkan nama siswa atau nomor aplikasi
        """
        filter_dict = {
            '$or': [
                {'student_name': {'$regex': query, '$options': 'i'}},
                {'application_number': {'$regex': query, '$options': 'i'}},
                {'parent_name': {'$regex': query, '$options': 'i'}}
            ]
        }
        
        if pesantren_id:
            filter_dict['pesantren_id'] = pesantren_id
        
        if status:
            filter_dict['status'] = status
        
        return self.find_many(filter_dict, [('created_at', -1)], limit)
    
    def cancel_application(self, application_id: str, reason: str = '') -> bool:
        """
        Batalkan aplikasi
        """
        update_data = {
            'status': 'cancelled',
            'cancelled_date': datetime.utcnow(),
            'cancellation_reason': reason,
            'updated_at': datetime.utcnow()
        }
        
        return self.update_by_id(application_id, update_data)
    
    def get_recent_applications(self, days: int = 7, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Mendapatkan aplikasi terbaru
        """
        since_date = datetime.utcnow() - timedelta(days=days)
        
        filter_dict = {
            'created_at': {'$gte': since_date}
        }
        
        return self.find_many(filter_dict, [('created_at', -1)], limit)