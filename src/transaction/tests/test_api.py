import pytest

from fastapi.testclient import TestClient
from main import app


def pytest_namespace():
    return {
        'user_id': None,
        'id': None,
    }


@pytest.mark.asyncio(loop_scope='session')
def test_create_transaction_valid_input(transaction_payload):
    with TestClient(app) as c:
        response = c.post(f"api/v1/transactions/", json=transaction_payload)
    assert response.status_code == 201

    response_json = response.json()
    assert response_json["user_id"] == transaction_payload["user_id"]
    assert response_json["transaction_currency"] == "USD"


def test_create_transaction_invalid_request():
    with TestClient(app=app) as c:
        response = c.post("api/v1/transactions", json={
            "user_id": "e7tyewrkjtty",
            "full_name": "Jane Doe",
            "transaction_amount": 475.66,
            "transaction_type": "cash",
            "transaction_date": "2024-10-05T09:40:53.695Z",
            "transaction_currency": "USD"
        })

    assert response.status_code == 422


def test_create_update_transaction(transaction_payload, transaction_payload_updated):
    with TestClient(app=app) as c:
        response = c.post("api/v1/transactions", json=transaction_payload)
        transaction_id = response.json().get("_id")

        assert response.status_code == 201

        # Update the created transaction
        response = c.put(
            f"/api/v1/transactions/{transaction_id}", json=transaction_payload_updated
        )
        assert response.status_code == 200
        response_json = response.json()
        assert response_json['data']['transaction_type'] == transaction_payload_updated['transaction_type']
        assert response_json['data']['user_id'] == transaction_payload['user_id']


def test_update_transaction_doesnt_exist(transaction_id, transaction_payload_updated):
    with TestClient(app=app, ) as c:
        response = c.put(f"api/v1/transactions/{transaction_id}", json=transaction_payload_updated)
        assert response.status_code == 404
        response_json = response.json()
        assert response_json["detail"] == f"Transaction not found"


def test_update_user_wrong_payload(transaction_id, transaction_payload_updated):
    with TestClient(app) as c:
        transaction_payload_updated["transaction_type"] = "cash"
        response = c.put(f"/api/v1/transactions/{transaction_id}", json=transaction_payload_updated)
        assert response.status_code == 422
        response_json = response.json()

        print(response_json)
        assert response_json == {
            "detail": [
                {
                    "type": "value_error",
                    "loc": ["body", "transaction_type"],
                    "msg": "Value error, value must be one of: ['debit', 'credit']",
                    "input": "cash",
                    "url": "https://errors.pydantic.dev/2.6/v/value_error",
                    "ctx": {"error": {}}
                }
            ]
        }


def test_create_delete_transaction(transaction_payload):
    with TestClient(app) as c:
        response = c.post(f"api/v1/transactions", json=transaction_payload)
        transaction_id = response.json().get("_id")
        assert response.status_code == 201

        response = c.delete(f"/api/v1/transactions/{transaction_id}")
        assert response.status_code == 204


@pytest.mark.asyncio
def test_fetch_transaction_history(transaction_payload):
    with TestClient(app) as c:
        response = c.post(f"api/v1/transactions", json=transaction_payload)
        data = response.json().get("data")
        user_id = data['user_id']
        assert response.status_code == 201

        response = c.get(f"/api/v1/transactions/{user_id}")
        assert response.status_code == 200


@pytest.mark.asyncio
def test_fetch_transaction_analytics(transaction_payload):
    with TestClient(app) as c:
        response = c.post(f"api/v1/transactions", json=transaction_payload)
        response = c.post(f"api/v1/transactions", json=transaction_payload)
        data = response.json().get("data")
        user_id = data['user_id']
        assert response.status_code == 201

        response = c.get(f"/api/v1/transactions/{user_id}/analytics")
        assert response.status_code == 200
        response_json = response.json()
        assert float(response_json['data']['average_transaction_value']) == transaction_payload['transaction_amount']
