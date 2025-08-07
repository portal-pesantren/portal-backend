#!/usr/bin/env python3
import sys
sys.path.append('.')

from dto.user_dto import UserRegistrationDTO
from pydantic import ValidationError

def test_phone_validation():
    test_cases = [
        "+62-812-3456-7899",
        "+6281234567899",
        "081234567899",
        "0812-3456-7899"
    ]
    
    for phone in test_cases:
        print(f"\nTesting phone: {phone}")
        try:
            dto = UserRegistrationDTO(
                name="Test User",
                email="test@example.com",
                password="testpassword123",
                confirm_password="testpassword123",
                phone=phone,
                terms_accepted=True
            )
            print(f"✓ Valid: {phone} -> {dto.phone}")
        except ValidationError as e:
            print(f"✗ Invalid: {phone}")
            print(f"Error: {e}")
        except Exception as e:
            print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    test_phone_validation()