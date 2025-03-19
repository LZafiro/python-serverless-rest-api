import logging
from typing import Dict, List, Optional, Any
import hashlib
import os

from src.domain.models.user import User
from src.repositories.user_repository import UserRepository
from src.core.exceptions import BusinessError, NotFoundError

logger = logging.getLogger(__name__)

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    def create_user(self, user_data: Dict[str, Any]) -> User:
        required_fields = ['email', 'first_name', 'last_name', 'password']
        for field in required_fields:
            if field not in user_data or not user_data[field]:
                raise BusinessError(f"Missing required field: {field}")

        existing_user = self.user_repository.find_by_email(user_data['email'])
        if existing_user:
            raise BusinessError(f"User with email {user_data['email']} already exists")

        password = user_data.pop('password')
        password_hash = self._hash_password(password)

        user = User.from_dict(user_data)
        user.password_hash = password_hash

        return self.user_repository.create_user(user)

    def get_user(self, user_id: str) -> User:
        user = self.user_repository.get_user_or_error(user_id)
        return user

    def list_users(self, limit: int = 100, offset: int = 0, is_active: Optional[bool] = None) -> List[User]:
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active

        return self.user_repository.list_users(limit, offset, filters)

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> User:
        existing_user = self.user_repository.get_user_or_error(user_id)

        if not existing_user:
            raise BusinessError(f"User not found")

        if 'password' in update_data:
            password = update_data.pop('password')
            update_data['password_hash'] = self._hash_password(password)

        if 'email' in update_data and update_data['email'] != existing_user.email:
            existing_email_user = self.user_repository.find_by_email(update_data['email'])
            if existing_email_user:
                raise BusinessError(f"User with email {update_data['email']} already exists")

        return self.user_repository.update_user(user_id, update_data)

    def delete_user(self, user_id: str) -> bool:
        return self.user_repository.delete_user(user_id)

    def _hash_password(self, password: str) -> str:
        # In a real application, shpuld use a proper password hashing library (bcrypt)
        salt = os.environ.get('PASSWORD_SALT', 'default-salt-value')
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
