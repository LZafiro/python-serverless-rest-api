from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class CreateUserRequest:
    """Schema for user creation request."""
    email: str
    first_name: str
    last_name: str
    password: str
    is_active: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CreateUserRequest':
        # Filter to only valid fields
        valid_fields = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_fields)

    def to_domain_dict(self) -> Dict[str, Any]:
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password': self.password,
            'is_active': self.is_active
        }


@dataclass
class UpdateUserRequest:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UpdateUserRequest':
        # Filter to only valid fields
        valid_fields = {k: v for k, v in data.items() if k in cls.__annotations__}
        return cls(**valid_fields)

    def to_domain_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class UserResponse:
    id: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    @classmethod
    def from_domain(cls, user) -> 'UserResponse':
        user_dict = user.to_response_dict()

        # Convert datetime to iso strings
        if isinstance(user_dict.get('created_at'), datetime):
            user_dict['created_at'] = user_dict['created_at'].isoformat()
        if isinstance(user_dict.get('updated_at'), datetime):
            user_dict['updated_at'] = user_dict['updated_at'].isoformat()

        return cls(**user_dict)


@dataclass
class UsersListResponse:
    items: List[UserResponse]
    total: int
    limit: int
    offset: int


@dataclass
class ErrorResponse:
    error: str
    message: str
    status_code: int
