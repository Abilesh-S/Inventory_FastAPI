def test_sell_stock_as_employee_success(
    client,
    admin_headers,
    employee_headers,
    sample_product,
):
    add_response = client.post(
        f"/admin/products/{sample_product['id']}/add-stock",
        headers=admin_headers,
        json={"quantity": 100},
    )

    assert add_response.status_code == 200

    response = client.post(
        "/employee/sell",
        headers=employee_headers,
        json={
            "product_id": sample_product["id"],
            "quantity": 10,
        },
    )

    assert response.status_code == 200
    assert response.json()["transaction_type"] == "SALE"
    assert response.json()["quantity"] == 10


def test_sell_stock_as_admin_also_allowed(
    client,
    admin_headers,
    sample_product,
):
    client.post(
        f"/admin/products/{sample_product['id']}/add-stock",
        headers=admin_headers,
        json={"quantity": 50},
    )

    response = client.post(
        "/employee/sell",
        headers=admin_headers,
        json={
            "product_id": sample_product["id"],
            "quantity": 5,
        },
    )

    assert response.status_code == 200


def test_sell_insufficient_stock(
    client,
    admin_headers,
    employee_headers,
    sample_product,
):
    client.post(
        f"/admin/products/{sample_product['id']}/add-stock",
        headers=admin_headers,
        json={"quantity": 5},
    )

    response = client.post(
        "/employee/sell",
        headers=employee_headers,
        json={
            "product_id": sample_product["id"],
            "quantity": 1000,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Insufficient stock"


def test_sell_product_not_found(
    client,
    employee_headers,
):
    response = client.post(
        "/employee/sell",
        headers=employee_headers,
        json={
            "product_id": 99999,
            "quantity": 1,
        },
    )

    assert response.status_code == 404


def test_sell_no_auth(
    client,
    sample_product,
):
    response = client.post(
        "/employee/sell",
        json={
            "product_id": sample_product["id"],
            "quantity": 1,
        },
    )

    assert response.status_code == 401


def test_sell_with_customer_id(
    client,
    admin_headers,
    employee_headers,
    sample_product,
):
    client.post(
        f"/admin/products/{sample_product['id']}/add-stock",
        headers=admin_headers,
        json={"quantity": 50},
    )

    customer_response = client.post(
        "/customers/",
        headers=employee_headers,
        json={
            "name": "John Doe",
            "phone": "9999999999",
            "address": "Chennai",
        },
    )

    assert customer_response.status_code == 200

    customer = customer_response.json()

    response = client.post(
        "/employee/sell",
        headers=employee_headers,
        json={
            "product_id": sample_product["id"],
            "quantity": 5,
            "customer_id": customer["id"],
        },
    )

    assert response.status_code == 200
    assert response.json()["customer_id"] == customer["id"]


def test_sell_zero_quantity(
    client,
    employee_headers,
    sample_product,
):
    response = client.post(
        "/employee/sell",
        headers=employee_headers,
        json={
            "product_id": sample_product["id"],
            "quantity": 0,
        },
    )

    assert response.status_code == 422


def test_sell_negative_quantity(
    client,
    employee_headers,
    sample_product,
):
    response = client.post(
        "/employee/sell",
        headers=employee_headers,
        json={
            "product_id": sample_product["id"],
            "quantity": -10,
        },
    )

    assert response.status_code == 422