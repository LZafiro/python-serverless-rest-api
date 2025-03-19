import pytest
from unittest.mock import Mock, patch
from datetime import datetime
import uuid

from src.domain.services.user_service import UserService
from src.domain.models.user import User
from src.core.exceptions import BusinessError, NotFoundError


@pytest.fixture
def mock_user_repository():
    return Mock()


@pytest.fixture
def user_service(mock_user_repository):
    return UserService(mock_user_repository)


def test_create_user_success(user_service, mock_user_repository):
    """Test create user success."""

    user_data = {
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'password123'
    }

    mock_user_repository.find_by_email.return_value = None

    expected_user = User(
        id=str(uuid.uuid4()),
        email=user_data['email'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    mock_user_repository.create_user.return_value = expected_user

    result = user_service.create_user(user_data)

    assert result == expected_user
    mock_user_repository.find_by_email.assert_called_once_with(user_data['email'])
    mock_user_repository.create_user.assert_called_once()

    created_user = mock_user_repository.create_user.call_args[0][0]
    assert created_user.password_hash is not None
    assert created_user.password_hash != user_data['password']


def test_create_user_existing_email(user_service, mock_user_repository):
    """Test create user with existing email."""

    user_data = {
        'email': 'existing@example.com',
        'first_name': 'Existing',
        'last_name': 'User',
        'password': 'password123'
    }

    existing_user = User(
        id=str(uuid.uuid4()),
        email=user_data['email'],
        first_name='Other',
        last_name='User',
        is_active=True
    )
    mock_user_repository.find_by_email.return_value = existing_user

    with pytest.raises(BusinessError) as exc_info:
        user_service.create_user(user_data)

    assert "already exists" in str(exc_info.value)
    mock_user_repository.find_by_email.assert_called_once_with(user_data['email'])
    mock_user_repository.create_user.assert_not_called()


def test_get_user_success(user_service, mock_user_repository):
    """Test get user success."""

    user_id = str(uuid.uuid4())
    expected_user = User(
        id=user_id,
        email='test@example.com',
        first_name='Test',
        last_name='User',
        is_active=True
    )

    mock_user_repository.get_user_or_error.return_value = expected_user

    result = user_service.get_user(user_id)

    assert result == expected_user
    mock_user_repository.get_user_or_error.assert_called_once_with(user_id)


def test_get_user_not_found(user_service, mock_user_repository):
    """Test get user not found."""

    user_id = str(uuid.uuid4())

    mock_user_repository.get_user_or_error.side_effect = NotFoundError(f"User with id {user_id} not found")

    with pytest.raises(NotFoundError) as exc_info:
        user_service.get_user(user_id)

    assert str(user_id) in str(exc_info.value)
    mock_user_repository.get_user_or_error.assert_called_once_with(user_id)


def test_update_user_success(user_service, mock_user_repository):
    """Test update user success."""

    user_id = str(uuid.uuid4())
    existing_user = User(
        id=user_id,
        email='test@example.com',
        first_name='Test',
        last_name='User',
        is_active=True
    )

    update_data = {
        'first_name': 'Updated',
        'last_name': 'Name'
    }

    updated_user = User(
        id=user_id,
        email='test@example.com',
        first_name=update_data['first_name'],
        last_name=update_data['last_name'],
        is_active=True
    )

    mock_user_repository.get_user_or_error.return_value = existing_user
    mock_user_repository.update_user.return_value = updated_user

    result = user_service.update_user(user_id, update_data)

    assert result == updated_user
    mock_user_repository.get_user_or_error.assert_called_once_with(user_id)
    mock_user_repository.update_user.assert_called_once_with(user_id, update_data)
