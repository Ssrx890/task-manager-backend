from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from app.database import get_session
from app.api.deps import get_current_user
from app.models.user import User
from app.models.inventory import Product, ProductCreate, Category, CategoryCreate
from fastapi import UploadFile, File
import shutil
import uuid

router = APIRouter(prefix="/inventory", tags=["Inventario"])

# --- ENDPOINTS DE CATEGORÍAS ---

@router.post("/categories", response_model=Category)
def create_category(category_data: CategoryCreate, session: Session = Depends(get_session)):
    existing_category = session.exec(
        select(Category).where(Category.name == category_data.name)
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=400, 
            detail=f"La categoría '{category_data.name}' ya existe."
        )

    db_category = Category.model_validate(category_data)
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[Category])
def list_categories(session: Session = Depends(get_session)):
    return session.exec(select(Category)).all()


# --- ENDPOINTS DE PRODUCTOS ---

@router.post("/products", response_model=Product)
def create_product(
    product_data: ProductCreate, 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Crea un producto. Solo accesible por ADMIN."""
    if current_user.role != "ADMIN":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para gestionar productos"
        )
    
    # Validamos que la categoría exista antes de crear el producto
    category = session.get(Category, product_data.category_id)
    if not category:
        raise HTTPException(status_code=404, detail="La categoría especificada no existe")

    # Creamos el objeto de base de datos a partir del esquema de entrada
    db_product = Product.model_validate(product_data)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product

@router.get("/products", response_model=List[Product])
def list_products(session: Session = Depends(get_session)):
    return session.exec(select(Product)).all()

@router.post("/products/{product_id}/image")
def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Sube una imagen para un producto y guarda la ruta en la BD"""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # 1. Validar extensión (Solo imágenes)
    extension = file.filename.split(".")[-1].lower()
    if extension not in ["jpg", "jpeg", "png"]:
        raise HTTPException(status_code=400, detail="Formato de archivo no permitido")

    # 2. Crear nombre de archivo único
    filename = f"{uuid.uuid4()}.{extension}"
    file_path = f"static/{filename}"

    # 3. Guardar el archivo físicamente en el servidor
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 4. Guardar la URL en la base de datos
    product.image_url = f"/static/{filename}"
    session.add(product)
    session.commit()
    session.refresh(product)

    return {"message": "Imagen subida con éxito", "url": product.image_url}