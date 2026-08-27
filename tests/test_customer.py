def test_create_customer_missing_phone(
    client,
    admin_headers,
):
    response = client.post(
        "/customers/",
        headers=admin_headers,
        json={
            "name": "John Doe",
        },
    )

    assert response.status_code == 422