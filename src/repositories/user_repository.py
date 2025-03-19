from typing import Dict, List, Optional, Any
import logging

from src.core.db import Database
from src.repositories.base_repository import BaseRepository
from src.domain.models.user import User
from src.core.exceptions import RepositoryError, NotFoundError

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository):
    def __init__(self, db: Database):
        super().__init__(db, 'users')

    def create_user(self, user: User) -> User:
        try:
            user_dict = user.to_dict()
            # Remove id if None, db will create it
            if user_dict.get('id') is None:
                user_dict.pop('id', None)

            if user.password_hash:
                user_dict['password_hash'] = user.password_hash

            result = self.create(user_dict)
            return User.from_dict(result)
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise RepositoryError(f"Failed to create user: {str(e)}")

    def find_by_email(self, email: str) -> Optional[User]:
        query = f"SELECT * FROM {self.table_name} WHERE email = %(email)s"
        result = self.db.fetch_one(query, {'email': email})

        if not result:
            return None

        return User.from_dict(result)

    def get_user(self, user_id: str) -> Optional[User]:
        result = self.find_by_id(user_id)
        if not result:
            return None

        return User.from_dict(result)

    def get_user_or_error(self, user_id: str) -> User:
        result = self.find_by_id_or_error(user_id)
        return User.from_dict(result)

    def list_users(self, limit: int = 100, offset: int = 0, filters: Optional[Dict[str, Any]] = None) -> List[User]:
        results = self.find_all(filters, limit, offset)
        return [User.from_dict(user_dict) for user_dict in results]

    def update_user(self, user_id: str, update_data: Dict[str, Any]) -> User:
        result = self.update(user_id, update_data)
        return User.from_dict(result)

    def delete_user(self, user_id: str) -> bool:
        return self.delete(user_id)
