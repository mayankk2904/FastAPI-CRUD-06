import pytest

@pytest.fixture(scope="module")
def created_user(client):
    response = client.post(
        "/users",
        json={
            "name": "Omkar",
            "email": "omkar@gmail.com",
            "age": 21,
            "marks": 96.5
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "id" in data

    return data


def test_get_all_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
-
def test_get_single_user(client, created_user):
    user_id = created_user["id"]
    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_update_user(client, created_user):
    user_id = created_user["id"]

    response = client.put(
        f"/users/{user_id}",
        json={
            "name": "Omkar Updated",
            "email": "omkar_updated@gmail.com",
            "age": 22,
            "marks": 98
        }
    )

    assert response.status_code == 200
    assert response.json()["name"] == "Omkar Updated"


def test_delete_user(client, created_user):
    user_id = created_user["id"]

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"


def test_bulk_insert_users(client):
    response = client.post(
        "/users/bulk",
        json={
            "users": [
                {
                    "name": "Zain",
                    "email": "zain@gmail.com",
                    "age": 21,
                    "marks": 95
                },
                {
                    "name": "Kushal",
                    "email": "kushal@gmail.com",
                    "age": 22,
                    "marks": 92
                },
                {
                    "name": "Ahan",
                    "email": "ahan@gmail.com",
                    "age": 23,
                    "marks": 90
                }
            ]
        }
    )

    assert response.status_code == 200
    assert len(response.json()) == 3
