from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection
from pymongo.results import InsertOneResult, UpdateResult, DeleteResult
from core.db import get_collection
import logging

logger = logging.getLogger(__name__)

class BaseModel(ABC):
    """
    Base model class untuk semua model MongoDB
    """
    
    def __init__(self, collection_name: str):
        self.collection_name = collection_name
        self.collection: Collection = get_collection(collection_name)
    
    def _prepare_document(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mempersiapkan dokumen sebelum disimpan ke database
        """
        # Tambahkan timestamp jika belum ada
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        
        data['updated_at'] = datetime.utcnow()
        
        # Hapus field None
        return {k: v for k, v in data.items() if v is not None}
    
    def _convert_object_id(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Konversi ObjectId ke string untuk response JSON
        """
        if doc and '_id' in doc:
            doc['id'] = str(doc['_id'])
            del doc['_id']
        return doc
    
    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Membuat dokumen baru
        """
        try:
            prepared_data = self._prepare_document(data)
            result: InsertOneResult = self.collection.insert_one(prepared_data)
            
            # Ambil dokumen yang baru dibuat
            created_doc = self.collection.find_one({'_id': result.inserted_id})
            return self._convert_object_id(created_doc)
            
        except Exception as e:
            logger.error(f"Error creating document in {self.collection_name}: {str(e)}")
            raise
    
    def find_by_id(self, doc_id: Union[str, ObjectId]) -> Optional[Dict[str, Any]]:
        """
        Mencari dokumen berdasarkan ID
        """
        try:
            if isinstance(doc_id, str):
                doc_id = ObjectId(doc_id)
            
            doc = self.collection.find_one({'_id': doc_id})
            return self._convert_object_id(doc) if doc else None
            
        except Exception as e:
            logger.error(f"Error finding document by ID in {self.collection_name}: {str(e)}")
            return None
    
    def find_one(self, filter_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Mencari satu dokumen berdasarkan filter
        """
        try:
            doc = self.collection.find_one(filter_dict)
            return self._convert_object_id(doc) if doc else None
            
        except Exception as e:
            logger.error(f"Error finding document in {self.collection_name}: {str(e)}")
            return None
    
    def find_many(self, 
                  filter_dict: Dict[str, Any] = None, 
                  sort: List[tuple] = None,
                  limit: int = None,
                  skip: int = None) -> List[Dict[str, Any]]:
        """
        Mencari banyak dokumen berdasarkan filter
        """
        try:
            if filter_dict is None:
                filter_dict = {}
            
            cursor = self.collection.find(filter_dict)
            
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            docs = list(cursor)
            return [self._convert_object_id(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Error finding documents in {self.collection_name}: {str(e)}")
            return []
    
    def update_by_id(self, doc_id: Union[str, ObjectId], data: Dict[str, Any]) -> bool:
        """
        Update dokumen berdasarkan ID
        """
        try:
            if isinstance(doc_id, str):
                doc_id = ObjectId(doc_id)
            
            # Tambahkan updated_at
            data['updated_at'] = datetime.utcnow()
            
            result: UpdateResult = self.collection.update_one(
                {'_id': doc_id},
                {'$set': data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating document in {self.collection_name}: {str(e)}")
            return False
    
    def delete_by_id(self, doc_id: Union[str, ObjectId]) -> bool:
        """
        Hapus dokumen berdasarkan ID
        """
        try:
            if isinstance(doc_id, str):
                doc_id = ObjectId(doc_id)
            
            result: DeleteResult = self.collection.delete_one({'_id': doc_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting document in {self.collection_name}: {str(e)}")
            return False
    
    def count(self, filter_dict: Dict[str, Any] = None) -> int:
        """
        Menghitung jumlah dokumen
        """
        try:
            if filter_dict is None:
                filter_dict = {}
            return self.collection.count_documents(filter_dict)
            
        except Exception as e:
            logger.error(f"Error counting documents in {self.collection_name}: {str(e)}")
            return 0
    
    def aggregate(self, pipeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Menjalankan aggregation pipeline
        """
        try:
            cursor = self.collection.aggregate(pipeline)
            docs = list(cursor)
            return [self._convert_object_id(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Error running aggregation in {self.collection_name}: {str(e)}")
            return []
    
    def search_text(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Pencarian teks menggunakan text index
        """
        try:
            cursor = self.collection.find(
                {'$text': {'$search': query}},
                {'score': {'$meta': 'textScore'}}
            ).sort([('score', {'$meta': 'textScore'})]).limit(limit)
            
            docs = list(cursor)
            return [self._convert_object_id(doc) for doc in docs]
            
        except Exception as e:
            logger.error(f"Error searching text in {self.collection_name}: {str(e)}")
            return []
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validasi data sebelum disimpan
        Harus diimplementasikan oleh setiap model
        """
        pass