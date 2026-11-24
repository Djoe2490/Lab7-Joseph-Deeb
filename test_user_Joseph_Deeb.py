import pytest

import app


@pytest.fixture(autouse=True)
def reset_database():
    connection = app.get_db_connection()
    connection.execute("DELETE FROM users")
    connection.execute("DELETE FROM sqlite_sequence WHERE name = 'users'")
    connection.executemany(
        "INSERT INTO users (name, email) VALUES (?, ?)",
        [("Alice", "alice@example.com"), ("Bob", "bob@example.com")],
    )
    connection.commit()
    connection.close()


@pytest.fixture
def client():
    app.app.config.update(TESTING=True)
    return app.app.test_client()


def test_database_is_created_with_specified_users():
    users = app.Get_users()

    assert len(users) == 2
    assert {user["name"] for user in users} == {"Alice", "Bob"}


def test_insert_user():
    user_id = app.Insert_user("Carol", "carol@example.com")

    assert app.Get_users_by_id(user_id)["name"] == "Carol"


def test_get_users():
    users = app.Get_users()

    assert isinstance(users, list)
    assert len(users) == 2


def test_get_users_by_id():
    user = app.Get_users_by_id(1)

    assert user is not None
    assert user["name"] == "Alice"


def test_update_user():
    assert app.Update_user(1, "Alice Updated", "alice.updated@example.com")

    user = app.Get_users_by_id(1)
    assert user["name"] == "Alice Updated"
    assert user["email"] == "alice.updated@example.com"


def test_delete_user():
    assert app.Delete_user(2)
    assert app.Get_users_by_id(2) is None


def test_api_get_user(client):
    response = client.get("/api/users")

    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2


def test_api_add_user(client):
    response = client.post(
        "/api/users",
        json={"name": "Carol", "email": "carol@example.com"},
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Carol"
    assert data["email"] == "carol@example.com"


def test_api_update_user(client):
    response = client.put(
        "/api/users/1",
        json={"name": "Alice Updated", "email": "alice.updated@example.com"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["name"] == "Alice Updated"
    assert data["email"] == "alice.updated@example.com"


def test_api_delete_user(client):
    response = client.delete("/api/users/2")

    assert response.status_code == 200
    assert response.get_json()["deleted"] is True
    assert app.Get_users_by_id(2) is None
