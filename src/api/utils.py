import json
from typing import Dict, Any, Optional, Union, List
import logging
from functools import wraps

from src.core.exceptions import AppException, ValidationError

logger = logging.getLogger(__name__)

def build_response(status_code: int, body: Union[Dict[str, Any], List[Any]], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """
    Build a standardized Lambda proxy response.
    """
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',  # To support Cors
        'Access-Control-Allow-Credentials': 'true'
    }

    response_headers = {**default_headers, **(headers or {})}

    return {
        'statusCode': status_code,
        'headers': response_headers,
        'body': json.dumps(body, default=str)
    }


def handle_exceptions(func):
    @wraps(func)
    def wrapper(event, context):
        try:
            return func(event, context)
        except AppException as e:
            logger.warning(f"Application exception: {str(e)}", exc_info=True)
            return build_response(
                e.status_code,
                {'error': e.error_code, 'message': e.message, 'status_code': e.status_code}
            )
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            return build_response(
                500,
                {'error': 'internal_error', 'message': 'An unexpected error occurred', 'status_code': 500}
            )
    return wrapper


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get('body')

    if not body:
        raise ValidationError("Request body is required")

    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in request body: {str(e)}")


def get_path_parameter(event: Dict[str, Any], param_name: str) -> str:
    path_parameters = event.get('pathParameters') or {}
    param_value = path_parameters.get(param_name)

    if not param_value:
        raise ValidationError(f"Missing path parameter: {param_name}")

    return param_value


def get_query_parameters(event: Dict[str, Any]) -> Dict[str, str]:
    return event.get('queryStringParameters') or {}


def parse_pagination_params(query_params: Dict[str, str]) -> Dict[str, int]:
    try:
        limit = int(query_params.get('limit', '100'))
        # Set a max for the limit
        limit = min(max(1, limit), 1000)
    except ValueError:
        limit = 100

    try:
        offset = int(query_params.get('offset', '0'))
        offset = max(0, offset)
    except ValueError:
        offset = 0

    return {'limit': limit, 'offset': offset}
