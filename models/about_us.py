from typing import Dict, Any, Optional
from .base import BaseModel
from pymongo.collection import ReturnDocument
from datetime import datetime, timezone 

class AboutUsModel(BaseModel):
    """
    Model untuk data 'About Us' yang bersifat singleton.
    """
    def __init__(self):
        # Nama koleksi di MongoDB
        super().__init__('about_us')

    def validate_data(self, data: Dict[str, Any]) -> bool:
        # Hapus 'images' dari validasi karena sekarang opsional
        if 'description' not in data or 'why_us' not in data:
            return False
        # Cek tipe data image_url jika ada
        if 'image_url' in data and data['image_url'] is not None and not isinstance(data['image_url'], str):
            return False
        return True

    def get_about_us(self) -> Optional[Dict[str, Any]]:
        """Mengambil satu-satunya dokumen 'About Us'."""
        doc = self.collection.find_one({})
        return self._convert_object_id(doc) if doc else None

    def update_about_us(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Memperbarui atau membuat (upsert) dokumen 'About Us'
        dengan timestamp yang dibuat di Python.
        """
        now = datetime.now(timezone.utc)
        
        data_to_set = data.copy()
        data_to_set['updated_at'] = now

        update_instruction = {
            '$set': data_to_set,
            '$setOnInsert': { 'created_at': now }
        }

        updated_doc = self.collection.find_one_and_update(
            {},
            update_instruction,
            upsert=True,
            return_document=ReturnDocument.AFTER
        )
        return self._convert_object_id(updated_doc)