import os
import uuid
import asyncio

import pytest


# @pytest.fixture(scope="session")
# def event_loop():
#     """Create an instance of the event loop for tests."""
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


# Fixture to generate a random user id
@pytest.fixture()
def user_id() -> str:
    """Generate a random user id."""
    return str(uuid.uuid4())


@pytest.fixture()
def transaction_id() -> str:
    return os.urandom(12).hex()


# Fixture to generate a user payload
@pytest.fixture()
def transaction_payload(user_id):
    """Generate a user payload."""
    return {
        "user_id": user_id,
        "full_name": "Jane Doe",
        "transaction_amount": 475.66,
        "transaction_type": "credit",
        "transaction_date": "2024-10-05T09:40:53.695Z",
        "transaction_currency": "USD"
    }


@pytest.fixture()
def transaction_payload_updated():
    """Generate a user payload."""
    return {
        "full_name": "Jane Doe",
        "transaction_amount": 500.66,
        "transaction_type": "debit",
        "transaction_date": "2024-10-05T09:40:53.695Z",
        "transaction_currency": "USD"
    }
