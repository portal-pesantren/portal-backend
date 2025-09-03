from .base import BaseModel
from datetime import datetime, timezone
import pymongo

class TokenBlocklistModel(BaseModel):
    def __init__(self):
        super().__init__('token_blocklist')
        # Buat TTL Index agar MongoDB otomatis menghapus token yang sudah kedaluwarsa dari blocklist
        try:
            self.collection.create_index("expires_at", expireAfterSeconds=0)
        except pymongo.errors.OperationFailure:
            # Index mungkin sudah ada, abaikan error
            pass

    def block_token(self, jti: str, expires_at: datetime) -> bool:
        """Menambahkan jti token ke daftar blokir."""
        try:
            self.collection.insert_one({
                "jti": jti,
                "created_at": datetime.now(timezone.utc),
                "expires_at": expires_at
            })
            return True
        except Exception:
            return False

    def is_token_blocked(self, jti: str) -> bool:
        """Memeriksa apakah jti token ada di daftar blokir."""
        return self.collection.find_one({"jti": jti}) is not None
    
    # Override fungsi ini karena collection ini tidak butuh validasi kompleks
    def validate_data(self, data) -> bool:
        return True