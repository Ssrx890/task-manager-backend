import os
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlmodel import Session, select

from app.database import get_session
from app.api.deps import get_current_user, get_admin_user
from app.models.user import User
from app.models.inventory import Product, ProductCreate, Category, CategoryCreate
from app.models.schemas import ProductUpdate, CategoryUpdate

router = APIRouter(prefix="/inventory", tags=["Inventario"])


# ============================================================
#  CATEGORÍAS
# ============================================================

@router.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
def create_category(
    data: CategoryCreate,
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    """Crea una nueva categoría (solo ADMIN)."""
    existing = session.exec(select(Category).where(Category.name == data.name)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")

    category = Category(name=data.name, description=data.description)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@router.get("/categories", response_model=List[Category])
def list_categories(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Lista todas las categorías activas."""
    return session.exec(select(Category).where(Category.is_active == True)).all()


@router.put("/categories/{category_id}", response_model=Category)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    """Actualiza una categoría (solo ADMIN)."""
    category = session.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    session.add(category)
    session.commit()
    session.refresh(category)
    return category


# ============================================================
#  PRODUCTOS
# ============================================================

@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    """Crea un nuevo producto (solo ADMIN)."""
    existing = session.exec(select(Product).where(Product.sku == data.sku)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un producto con ese SKU")

    category = session.get(Category, data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    product = Product(**data.model_dump())
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.get("/products", response_model=List[Product])
def list_products(
    search: Optional[str] = Query(None, description="Buscar por nombre"),
    category_id: Optional[int] = Query(None, description="Filtrar por categoría"),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Lista productos activos con filtros opcionales."""
    query = select(Product).where(Product.is_active == True)

    if search:
        query = query.where(Product.name.contains(search))
    if category_id:
        query = query.where(Product.category_id == category_id)

    return session.exec(query).all()


@router.get("/products/{product_id}", response_model=Product)
def get_product(
    product_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Obtiene un producto por su ID."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product


@router.put("/products/{product_id}", response_model=Product)
def update_product(
    product_id: int,
    data: ProductUpdate,
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    """Actualiza un producto (solo ADMIN)."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    update_data = data.model_dump(exclude_unset=True)

    if "sku" in update_data:
        duplicate = session.exec(
            select(Product).where(Product.sku == update_data["sku"], Product.id != product_id)
        ).first()
        if duplicate:
            raise HTTPException(status_code=400, detail="Ya existe otro producto con ese SKU")

    for key, value in update_data.items():
        setattr(product, key, value)

    session.add(product)
    session.commit()
    session.refresh(product)
    return product


@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    """Soft-delete: desactiva un producto (solo ADMIN)."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    product.is_active = False
    session.add(product)
    session.commit()
    return


@router.post("/products/{product_id}/image", response_model=Product)
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    """Sube una imagen para un producto (solo ADMIN)."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if file.content_type not in ("image/jpeg", "image/png", "image/webp"):
        raise HTTPException(status_code=400, detail="Solo se permiten imágenes JPEG, PNG o WebP")

    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join("static", filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    product.image_url = f"/static/{filename}"
    session.add(product)
    session.commit()
    session.refresh(product)
    return product