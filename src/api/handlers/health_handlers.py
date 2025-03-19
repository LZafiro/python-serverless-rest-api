import logging
from datetime import datetime
from typing import Dict, Any

from src.core.container import DIContainer
from src.core.db import Database
from src.api.utils import handle_exceptions, build_response

logger = logging.getLogger(__name__)

container = DIContainer()
container.register(Database)


@handle_exceptions
def health_check(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    db = container.resolve(Database)

    db_status = "healthy"
    try:
        # To check db connection
        db.fetch_one("SELECT 1")
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"

    response = {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": db_status
        }
    }

    status_code = 200 if db_status == "healthy" else 503
    return build_response(status_code, response)
