from tests.conftest import auth_header
from app.core.security import get_password_hash
from app.models.user import User
from app.models.inventory import Category, Product


def _setup_product(session):
    """Helper: crea categoría y producto en la BD."""
    cat = Category(name="Electrónica", description="...")
    session.add(cat)
    session.commit()
    session.refresh(cat)

    prod = Product(name="Laptop", sku="LAP-001", price=500.0, stock=10, category_id=cat.id)
    session.add(prod)
    session.commit()
    session.refresh(prod)
    return prod


def test_add_item_to_cart(client, seller_token, session):
    prod = _setup_product(session)
    resp = client.post(
        f"/cart/items?product_id={prod.id}&quantity=3",
        headers=auth_header(seller_token),
    )
    assert resp.status_code == 200
    assert len(resp.json()["items"]) == 1


def test_add_item_over_stock(client, seller_token, session):
    prod = _setup_product(session)
    resp = client.post(
        f"/cart/items?product_id={prod.id}&quantity=999",
        headers=auth_header(seller_token),
    )
    assert resp.status_code == 400


def test_get_cart(client, seller_token, session):
    _setup_product(session)
    resp = client.get("/cart/", headers=auth_header(seller_token))
    assert resp.status_code == 200


def test_remove_item_from_cart(client, seller_token, session):
    prod = _setup_product(session)
    client.post(f"/cart/items?product_id={prod.id}&quantity=1", headers=auth_header(seller_token))
    resp = client.delete(f"/cart/items/{prod.id}", headers=auth_header(seller_token))
    assert resp.status_code == 204


def test_clear_cart(client, seller_token, session):
    prod = _setup_product(session)
    client.post(f"/cart/items?product_id={prod.id}&quantity=1", headers=auth_header(seller_token))
    resp = client.delete("/cart/", headers=auth_header(seller_token))
    assert resp.status_code == 204
