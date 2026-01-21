from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ...database import get_session
from ...models.user import User, UserCreate, UserResponse, Token
from ...core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """Registra un nuevo usuario en el sistema"""
    # Verificamos si el email ya existe
    statement = select(User).where(User.email == user_data.email)
    user_exists = session.exec(statement).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Creamos el objeto de base de datos
    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role=user_data.role,
        hashed_password=get_password_hash(user_data.password) # Encriptamos
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