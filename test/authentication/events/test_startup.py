import pytest
from unittest.mock import AsyncMock, patch

# Assuming your create_default_users function is located here:
# Adjust the import path as needed for your project structure
from ....src.authentication.events.start_up import create_default_users 

# --- Fixtures for Mocking Dependencies ---

@pytest.fixture
def mock_users_collection():
    """Mock the MongoDB collection object with methods for finding and inserting."""
    mock_collection = AsyncMock()
    # Configure the mock find_one method's return value for different scenarios
    # Default: Simulate that NO user exists (returns None)
    mock_collection.find_one.return_value = None
    return mock_collection

@pytest.fixture
def mock_pwd_context():
    """Mock the password hashing context, just returning the input as the 'hash' for simplicity."""
    mock_context = AsyncMock()
    mock_context.hash.side_effect = lambda password: f"hashed_{password}"
    return mock_context

# --- The Test Function ---

@pytest.mark.asyncio
async def test_create_default_users_inserts_new_users(mock_users_collection, mock_pwd_context):
    """
    Tests that the function inserts default users when they do not already exist.
    """
    
    # 1. Patch the global dependencies to use our mocks
    with patch('src.authentication.startup.users_collection', new=mock_users_collection), \
         patch('src.authentication.startup.pwd_context', new=mock_pwd_context):
        
        # 2. Execute the function under test
        await create_default_users()

    # 3. Assertions (Verifying the expected interactions with the mock database)

    # Check that find_one was called for both 'alice' and 'bob'
    expected_calls = [
        {"username": "alice"},
        {"username": "bob"}
    ]
    
    # Use assert_has_calls to check the find_one calls
    mock_users_collection.find_one.assert_any_call(expected_calls[0])
    mock_users_collection.find_one.assert_any_call(expected_calls[1])

    # Check that insert_one was called for both users with their hashed passwords
    mock_users_collection.insert_one.assert_any_call({
        "username": "alice", 
        "hashed_password": "hashed_alice123" # Uses the mock hash value
    })
    mock_users_collection.insert_one.assert_any_call({
        "username": "bob", 
        "hashed_password": "hashed_bob123" # Uses the mock hash value
    })
    
    # Check that insert_one was called exactly twice (for the two default users)
    assert mock_users_collection.insert_one.call_count == 2


@pytest.mark.asyncio
async def test_create_default_users_skips_existing_users(mock_users_collection, mock_pwd_context):
    """
    Tests that the function skips inserting users that already exist.
    """
    
    # Configure the mock to simulate that 'alice' EXISTS, but 'bob' does NOT
    mock_users_collection.find_one.side_effect = [
        {"username": "alice", "hashed_password": "existing_hash"}, # Return a user for the first call (alice)
        None # Return None for the second call (bob)
    ]

    # 1. Patch the dependencies
    with patch('src.authentication.startup.users_collection', new=mock_users_collection), \
         patch('src.authentication.startup.pwd_context', new=mock_pwd_context):
        
        # 2. Execute the function under test
        await create_default_users()

    # 3. Assertions
    
    # insert_one should only be called once, for 'bob' (the non-existing user)
    mock_users_collection.insert_one.assert_called_once_with({
        "username": "bob", 
        "hashed_password": "hashed_bob123"
    })
    
    # Verify the password context was only called for the user that was inserted (bob)
    assert mock_pwd_context.hash.call_count == 1