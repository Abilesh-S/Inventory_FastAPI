def test_audit_log_created_on_product_creation(client, admin_headers):
    client.post(
        "/admin/products",
        headers=admin_headers,
        json={"name": "Audit Test Item", "sku": "AUD-001", "price": 5.0, "quantity": 0},
    )
    response = client.get("/audit/", headers=admin_headers)
    assert response.status_code == 200
    actions = [entry["action"] for entry in response.json()]
    assert "PRODUCT_CREATED" in actions


def test_audit_log_created_on_stock_add(client, admin_headers, sample_product):
    client.post(f"/admin/products/{sample_product['id']}/add-stock", headers=admin_headers, json={"quantity": 20})

    response = client.get("/audit/", headers=admin_headers)
    actions = [entry["action"] for entry in response.json()]
    assert "STOCK_ADDED" in actions


def test_audit_log_created_on_sale(client, admin_headers, employee_headers, sample_product):
    client.post(f"/admin/products/{sample_product['id']}/add-stock", headers=admin_headers, json={"quantity": 20})
    client.post(
        "/employee/sell",
        headers=employee_headers,
        json={"product_id": sample_product["id"], "quantity": 5},
    )

    response = client.get("/audit/", headers=admin_headers)
    actions = [entry["action"] for entry in response.json()]
    assert "STOCK_SOLD" in actions


def test_audit_log_created_on_user_creation(client, admin_headers, employee_token):
    response = client.get("/audit/", headers=admin_headers)
    actions = [entry["action"] for entry in response.json()]
    assert "USER_CREATED" in actions


def test_audit_forbidden_for_employee(client, employee_headers):
    response = client.get("/audit/", headers=employee_headers)
    assert response.status_code == 403


def test_audit_requires_auth(client):
    response = client.get("/audit/")
    assert response.status_code == 401