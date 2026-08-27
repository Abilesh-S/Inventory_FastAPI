def test_create_product_as_admin(
    client,
    admin_headers,
):
    response = client.post(
        "/admin/products",
        headers=admin_headers,
        json={
            "name": "Laptop",
            "sku": "LAP-001",
            "price": 50000.0,
            "quantity": 10,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Laptop"
    assert data["sku"] == "LAP-001"
    assert data["price"] == 50000.0
    assert data["quantity"] == 10


def test_create_product_as_employee_forbidden(
    client,
    employee_headers,
):
    response = client.post(
        "/admin/products",
        headers=employee_headers,
        json={
            "name": "Laptop",
            "sku": "EMP-001",
            "price": 50000.0,
            "quantity": 10,
        },
    )

    assert response.status_code == 403


def test_create_product_without_auth(client):
    response = client.post(
        "/admin/products",
        json={
            "name": "Laptop",
            "sku": "NOAUTH-001",
            "price": 50000.0,
            "quantity": 10,
        },
    )

    assert response.status_code == 401


def test_create_product_duplicate_sku(
    client,
    admin_headers,
    sample_product,
):
    response = client.post(
        "/admin/products",
        headers=admin_headers,
        json={
            "name": "Another Widget",
            "sku": "TW-001",
            "price": 50.0,
            "quantity": 5,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "SKU already exists"


def test_add_stock_as_admin(
    client,
    admin_headers,
    sample_product,
):
    response = client.post(
        f"/admin/products/{sample_product['id']}/add-stock",
        headers=admin_headers,
        json={
            "quantity": 50,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["quantity"] == 50


def test_add_stock_as_employee_forbidden(
    client,
    employee_headers,
    sample_product,
):
    response = client.post(
        f"/admin/products/{sample_product['id']}/add-stock",
        headers=employee_headers,
        json={
            "quantity": 50,
        },
    )

    assert response.status_code == 403


def test_add_stock_without_auth(
    client,
    sample_product,
):
    response = client.post(
        f"/admin/products/{sample_product['id']}/add-stock",
        json={
            "quantity": 50,
        },
    )

    assert response.status_code == 401


def test_add_stock_product_not_found(
    client,
    admin_headers,
):
    response = client.post(
        "/admin/products/99999/add-stock",
        headers=admin_headers,
        json={
            "quantity": 50,
        },
    )

    assert response.status_code == 404