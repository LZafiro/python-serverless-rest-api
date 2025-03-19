import logging
from typing import Dict, Any

from src.core.container import DIContainer
from src.core.db import Database
from src.repositories.user_repository import UserRepository
from src.domain.services.user_service import UserService
from src.api.schemas.user_schemas import (
    CreateUserRequest,
    UpdateUserRequest,
    UserResponse,
    UsersListResponse
)
from src.api.utils import (
    handle_exceptions,
    build_response,
    parse_body,
    get_path_parameter,
    get_query_parameters,
    parse_pagination_params
)
from src.core.exceptions import ValidationError

logger = logging.getLogger(__name__)

# Set up dependency injection
container = DIContainer()
container.register(Database)
container.register(UserRepository)
container.register(UserService)


@handle_exceptions
def create_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    body = parse_body(event)

    try:
        user_data = CreateUserRequest.from_dict(body)
    except Exception as e:
        logger.warning(f"Invalid create user request: {str(e)}")
        raise ValidationError(f"Invalid request data: {str(e)}")

    user_service = container.resolve(UserService)
    user = user_service.create_user(user_data.to_domain_dict())

    return build_response(201, UserResponse.from_domain(user).__dict__)


@handle_exceptions
def get_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    user_id = get_path_parameter(event, 'userId')

    user_service = container.resolve(UserService)
    user = user_service.get_user(user_id)

    return build_response(200, UserResponse.from_domain(user).__dict__)


@handle_exceptions
def list_users(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    query_params = get_query_parameters(event)
    pagination = parse_pagination_params(query_params)

    is_active = None
    if 'is_active' in query_params:
        is_active_str = query_params['is_active'].lower()
        if is_active_str in ('true', '1'):
            is_active = True
        elif is_active_str in ('false', '0'):
            is_active = False

    user_service = container.resolve(UserService)
    users = user_service.list_users(
        limit=pagination['limit'],
        offset=pagination['offset'],
        is_active=is_active
    )

    user_repository = container.resolve(UserRepository)
    filters = {'is_active': is_active} if is_active is not None else None
    total = user_repository.count(filters)

    response = UsersListResponse(
        items=[UserResponse.from_domain(user) for user in users],
        total=total,
        limit=pagination['limit'],
        offset=pagination['offset']
    )

    return build_response(200, response.__dict__)


@handle_exceptions
def update_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    user_id = get_path_parameter(event, 'userId')

    body = parse_body(event)
    try:
        update_data = UpdateUserRequest.from_dict(body)
    except Exception as e:
        logger.warning(f"Invalid update user request: {str(e)}")
        raise ValidationError(f"Invalid request data: {str(e)}")

    user_service = container.resolve(UserService)
    user = user_service.update_user(user_id, update_data.to_domain_dict())

    return build_response(200, UserResponse.from_domain(user).__dict__)


@handle_exceptions
def delete_user(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    user_id = get_path_parameter(event, 'userId')

    user_service = container.resolve(UserService)
    user_service.delete_user(user_id)

    return build_response(204, {})
