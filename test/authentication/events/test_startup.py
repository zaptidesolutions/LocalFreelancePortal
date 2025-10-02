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

    assert mock_users_collection.find_one.called
    assert mock_users_collection.insert_one.called

@pytest.mark.asyncio
async def test_create_default_users_skips_existing_users(mock_users_collection, mock_pwd_context, capsys):
    # Simulate that both users already exist
    mock_users_collection.find_one.return_value = {"username": "alice", "hashed_password": "hashed_alice123"}

    with patch('authentication.events.start_up.users_collection', new=mock_users_collection), \
         patch('authentication.events.start_up.pwd_context', new=mock_pwd_context):
        await create_default_users()

    # insert_one should not be called since users exist
    assert not mock_users_collection.insert_one.called

    # Check that the print statement for existing users was called
    captured = capsys.readouterr()
    assert "User alice already exists" in captured.out
    assert "User bob already exists" in captured.out