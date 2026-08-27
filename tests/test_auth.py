def test_login_success(client, admin_token):
    assert admin_token is not None
    assert len(admin_token) > 10


def test_login_wrong_password(client, admin_token):
    response = client.post(
        "/auth/login",
        data={
            "username": "testadmin",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        data={
            "username": "ghost",
            "password": "whatever",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_create_user_without_token_fails(client):
    response = client.post(
        "/auth/create-user",
        json={
            "username": "newbie",
            "email": "newbie@test.com",
            "password": "pass123",
            "role": "EMPLOYEE",
        },
    )

    assert response.status_code == 401


def test_create_user_as_employee_forbidden(client, employee_headers):
    response = client.post(
        "/auth/create-user",
        headers=employee_headers,
        json={
            "username": "sneaky",
            "email": "sneaky@test.com",
            "password": "pass123",
            "role": "ADMIN",
        },
    )

    assert response.status_code == 403


def test_create_user_as_admin_success(client, admin_headers):
    response = client.post(
        "/auth/create-user",
        headers=admin_headers,
        json={
            "username": "newemployee",
            "email": "newemployee@test.com",
            "password": "pass123",
            "role": "EMPLOYEE",
        },
    )

    assert response.status_code == 200
    assert response.json()["role"] == "EMPLOYEE"


def test_create_user_duplicate_email(
    client,
    admin_headers,
    employee_token,
):
    response = client.post(
        "/auth/create-user",
        headers=admin_headers,
        json={
            "username": "dupe",
            "email": "employee@test.com",
            "password": "pass123",
            "role": "EMPLOYEE",
        },
    )

    assert response.status_code == 400


def test_create_user_duplicate_username(
    client,
    admin_headers,
    employee_token,
):
    response = client.post(
        "/auth/create-user",
        headers=admin_headers,
        json={
            "username": "testemployee",
            "email": "different@test.com",
            "password": "pass123",
            "role": "EMPLOYEE",
        },
    )

    assert response.status_code == 400


def test_invalid_jwt_fails(client):
    response = client.post(
        "/admin/products",
        headers={
            "Authorization": "Bearer this-is-not-a-valid-token"
        },
        json={
            "name": "Test",
            "sku": "INVALID-001",
            "price": 10.0,
            "quantity": 1,
        },
    )

    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    response = client.post(
        "/admin/products",
        json={
            "name": "Unauthorized Product",
            "sku": "UNAUTH-001",
            "price": 10.0,
            "quantity": 1,
        },
    )

    assert response.status_code == 401