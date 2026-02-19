from tests.conftest import auth_header
from app.models.inventory import Category, Product


def _setup_product(session, stock=10):
    cat = Category(name="Electrónica", description="...")
    session.add(cat)
    session.commit()
    session.refresh(cat)

    prod = Product(name="Laptop", sku="LAP-001", price=500.0, stock=stock, category_id=cat.id)
    session.add(prod)
    session.commit()
    session.refresh(prod)
    return prod


def test_create_order_from_cart(client, seller_token, session):
    prod = _setup_product(session)
    # Add to cart
    client.post(f"/cart/items?product_id={prod.id}&quantity=2", headers=auth_header(seller_token))
    # Create order from cart
    resp = client.post("/orders/from_cart?payment_type=CASH", headers=auth_header(seller_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "Venta realizada desde carrito"
    assert data["total"] > 0


def test_create_order_credit_requires_name(client, seller_token, session):
    prod = _setup_product(session)
    client.post(f"/cart/items?product_id={prod.id}&quantity=1", headers=auth_header(seller_token))
    resp = client.post("/orders/from_cart?payment_type=CREDIT", headers=auth_header(seller_token))
    assert resp.status_code == 400


def test_create_order_empty_cart(client, seller_token):
    resp = client.post("/orders/from_cart?payment_type=CASH", headers=auth_header(seller_token))
    assert resp.status_code == 400


def test_list_orders(client, seller_token, session):
    prod = _setup_product(session)
    client.post(f"/cart/items?product_id={prod.id}&quantity=1", headers=auth_header(seller_token))
    client.post("/orders/from_cart?payment_type=CASH", headers=auth_header(seller_token))

    resp = client.get("/orders/", headers=auth_header(seller_token))
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_get_invoice(client, seller_token, session):
    prod = _setup_product(session)
    client.post(f"/cart/items?product_id={prod.id}&quantity=1", headers=auth_header(seller_token))
    order_resp = client.post("/orders/from_cart?payment_type=CASH", headers=auth_header(seller_token))
    factura = order_resp.json()["factura"]

    # Get the order ID from list
    orders = client.get("/orders/", headers=auth_header(seller_token)).json()
    order_id = orders[0]["id"]

    resp = client.get(f"/orders/{order_id}/invoice", headers=auth_header(seller_token))
    assert resp.status_code == 200
    assert resp.json()["invoice_number"] == factura


def test_invoice_access_denied(client, seller_token, admin_token, session):
    prod = _setup_product(session)
    # Seller creates order
    client.post(f"/cart/items?product_id={prod.id}&quantity=1", headers=auth_header(seller_token))
    client.post("/orders/from_cart?payment_type=CASH", headers=auth_header(seller_token))
    orders = client.get("/orders/", headers=auth_header(seller_token)).json()
    order_id = orders[0]["id"]

    # Admin should have access
    resp = client.get(f"/orders/{order_id}/invoice", headers=auth_header(admin_token))
    assert resp.status_code == 200
