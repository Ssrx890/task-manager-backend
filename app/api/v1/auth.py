from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ...database import get_session
from ...models.user import User, UserCreate, UserResponse, Token
from ...core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    statement = select(User).where(User.email == user_data.email)
    if session.exec(statement).first():
        raise HTTPException(status_code=400, detail="El email ya existe")

    #Forzamos el rol a SELLER
    # No importa si el usuario envió "ADMIN" en el JSON, lo ignoramos.
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role="SELLER",
        hashed_password=get_password_hash(user_data.password)
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """Verifica credenciales y devuelve un token JWT"""
    # Buscamos al usuario
    statement = select(User).where(User.email == form_data.username)
    user = session.exec(statement).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Creamos el token incluyendo su rol
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/create-admin", response_model=UserResponse)
def create_another_admin(
    user_data: UserCreate, 
    current_user: User = Depends(get_current_user), 
    session: Session = Depends(get_session)
):
    """Solo un ADMIN puede crear otros ADMINs"""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="No tienes permisos para crear administradores")
        
    new_admin = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role="ADMIN", # Aquí sí permitimos ADMIN porque el que lo crea ya lo es
        hashed_password=get_password_hash(user_data.password)
    )
    session.add(new_admin)
    session.commit()
    session.refresh(new_admin)
    return new_admin