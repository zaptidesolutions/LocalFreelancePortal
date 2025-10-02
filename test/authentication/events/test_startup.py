import pytest
from unittest.mock import AsyncMock, patch

from authentication.events.start_up import create_default_users

@pytest.fixture
def mock_users_collection():
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = None
    return mock_collection

@pytest.fixture
def mock_pwd_context():
    mock_context = AsyncMock()
    mock_context.hash.side_effect = lambda password: f"hashed_{password}"
    return mock_context

@pytest.mark.asyncio
async def test_create_default_users_calls_insert_and_find(mock_users_collection, mock_pwd_context):
    with patch('authentication.events.start_up.users_collection', new=mock_users_collection), \
         patch('authentication.events.start_up.pwd_context', new=mock_pwd_context):
        await create_default_users()

    # Just verify that find_one and insert_one were called
    assert mock_users_collection.find_one.called
    assert mock_users_collection.insert_one.called