from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class User:
    email: str
    first_name: str
    last_name: str
    is_active: bool = True
    id: Optional[str] = None
    password_hash: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        # Filter out unknown fields
        valid_fields = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_fields)

    def to_dict(self) -> Dict[str, Any]:
        result = {
            'id': self.id,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
        }

        if self.created_at:
            result['created_at'] = self.created_at
        if self.updated_at:
            result['updated_at'] = self.updated_at

        return result

    def to_response_dict(self) -> Dict[str, Any]:
        # Excludes sensitive fields like password_hash, and makes any other processing...
        return self.to_dict()
