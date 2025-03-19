from typing import Dict, List, Optional, Type, TypeVar, Generic, Any
import uuid
from datetime import datetime

from src.core.db import Database
from src.core.exceptions import RepositoryError, NotFoundError

T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, db: Database, table_name: str):
        self.db = db
        self.table_name = table_name

    def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        record = data.copy()
        record['id'] = str(uuid.uuid4())
        record['created_at'] = datetime.utcnow()
        record['updated_at'] = record['created_at']

        columns = ', '.join(record.keys())
        placeholders = ', '.join([f'%({key})s' for key in record.keys()])

        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders}) RETURNING *"

        try:
            result = self.db.fetch_one(query, record)
            return result
        except Exception as e:
            raise RepositoryError(f"Failed to create record: {str(e)}")

    def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        query = f"SELECT * FROM {self.table_name} WHERE id = %(id)s"
        result = self.db.fetch_one(query, {'id': id})

        if not result:
            return None

        return result

    def find_by_id_or_error(self, id: str) -> Dict[str, Any]:
        result = self.find_by_id(id)

        if not result:
            raise NotFoundError(f"Record with id {id} not found")

        return result

    def find_all(self, filters: Optional[Dict[str, Any]] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        query_parts = [f"SELECT * FROM {self.table_name}"]
        params = {'limit': limit, 'offset': offset}

        if filters:
            where_clauses = []
            for key, value in filters.items():
                where_clauses.append(f"{key} = %({key})s")
                params[key] = value

            if where_clauses:
                query_parts.append("WHERE " + " AND ".join(where_clauses))

        # pafination
        query_parts.append("LIMIT %(limit)s OFFSET %(offset)s")

        query = " ".join(query_parts)

        try:
            return self.db.fetch_all(query, params)
        except Exception as e:
            raise RepositoryError(f"Failed to fetch records: {str(e)}")

    def update(self, id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        self.find_by_id_or_error(id)

        update_data = data.copy()
        update_data['updated_at'] = datetime.utcnow()

        set_clauses = [f"{key} = %({key})s" for key in update_data.keys()]

        if not set_clauses:
            return self.find_by_id(id)

        query = f"""
            UPDATE {self.table_name}
            SET {', '.join(set_clauses)}
            WHERE id = %(id)s
            RETURNING *
        """

        params = update_data.copy()
        params['id'] = id

        try:
            result = self.db.fetch_one(query, params)
            return result
        except Exception as e:
            raise RepositoryError(f"Failed to update record: {str(e)}")

    def delete(self, id: str) -> bool:
        self.find_by_id_or_error(id)

        query = f"DELETE FROM {self.table_name} WHERE id = %(id)s"

        try:
            self.db.execute(query, {'id': id})
            return True
        except Exception as e:
            raise RepositoryError(f"Failed to delete record: {str(e)}")

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        query_parts = [f"SELECT COUNT(*) as count FROM {self.table_name}"]
        params = {}

        if filters:
            where_clauses = []
            for key, value in filters.items():
                where_clauses.append(f"{key} = %({key})s")
                params[key] = value

            if where_clauses:
                query_parts.append("WHERE " + " AND ".join(where_clauses))

        query = " ".join(query_parts)

        try:
            result = self.db.fetch_one(query, params)
            return result['count'] if result else 0
        except Exception as e:
            raise RepositoryError(f"Failed to count records: {str(e)}")
