from tests.conftest import auth_header


def _create_category(client, admin_token, name="Electrónica"):
    return client.post(
        "/inventory/categories",
        json={"name": name, "description": f"Categoría {name}"},
        headers=auth_header(admin_token),
    )


def _create_product(client, admin_token, category_id, name="Laptop", sku="LAP-001"):
    return client.post(
        "/inventory/products",
        json={"name": name, "sku": sku, "price": 999.99, "stock": 50, "category_id": category_id},
        headers=auth_header(admin_token),
    )


# --- CATEGORÍAS ---

def test_create_category(client, admin_token):
    resp = _create_category(client, admin_token)
    assert resp.status_code == 201
    assert resp.json()["name"] == "Electrónica"


def test_create_category_duplicate(client, admin_token):
    _create_category(client, admin_token)
    resp = _create_category(client, admin_token)
    assert resp.status_code == 400


def test_create_category_requires_admin(client, seller_token):
    resp = client.post(
        "/inventory/categories",
        json={"name": "Test"},
        headers=auth_header(seller_token),
    )
    assert resp.status_code == 403


def test_list_categories(client, admin_token, seller_token):
    _create_category(client, admin_token, "Cat1")
    _create_category(client, admin_token, "Cat2")
    resp = client.get("/inventory/categories", headers=auth_header(seller_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_update_category(client, admin_token):
    cat = _create_category(client, admin_token).json()
    resp = client.put(
        f"/inventory/categories/{cat['id']}",
        json={"name": "Ropa"},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Ropa"


# --- PRODUCTOS ---

def test_create_product(client, admin_token):
    cat = _create_category(client, admin_token).json()
    resp = _create_product(client, admin_token, cat["id"])
    assert resp.status_code == 201
    assert resp.json()["name"] == "Laptop"


def test_create_product_duplicate_sku(client, admin_token):
    cat = _create_category(client, admin_token).json()
    _create_product(client, admin_token, cat["id"])
    resp = _create_product(client, admin_token, cat["id"])
    assert resp.status_code == 400


def test_list_products(client, admin_token, seller_token):
    cat = _create_category(client, admin_token).json()
    _create_product(client, admin_token, cat["id"], "P1", "SKU-1")
    _create_product(client, admin_token, cat["id"], "P2", "SKU-2")
    resp = client.get("/inventory/products", headers=auth_header(seller_token))
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_list_products_search(client, admin_token, seller_token):
    cat = _create_category(client, admin_token).json()
    _create_product(client, admin_token, cat["id"], "Laptop HP", "SKU-A")
    _create_product(client, admin_token, cat["id"], "Mouse", "SKU-B")
    resp = client.get("/inventory/products?search=Laptop", headers=auth_header(seller_token))
    assert len(resp.json()) == 1


def test_get_single_product(client, admin_token, seller_token):
    cat = _create_category(client, admin_token).json()
    prod = _create_product(client, admin_token, cat["id"]).json()
    resp = client.get(f"/inventory/products/{prod['id']}", headers=auth_header(seller_token))
    assert resp.status_code == 200
    assert resp.json()["sku"] == "LAP-001"


def test_update_product(client, admin_token):
    cat = _create_category(client, admin_token).json()
    prod = _create_product(client, admin_token, cat["id"]).json()
    resp = client.put(
        f"/inventory/products/{prod['id']}",
        json={"price": 1299.99},
        headers=auth_header(admin_token),
    )
    assert resp.status_code == 200
    assert resp.json()["price"] == 1299.99


def test_delete_product_soft(client, admin_token, seller_token):
    cat = _create_category(client, admin_token).json()
    prod = _create_product(client, admin_token, cat["id"]).json()
    resp = client.delete(f"/inventory/products/{prod['id']}", headers=auth_header(admin_token))
    assert resp.status_code == 204
    # Producto ya no aparece en listado activo
    resp = client.get("/inventory/products", headers=auth_header(seller_token))
    assert len(resp.json()) == 0
