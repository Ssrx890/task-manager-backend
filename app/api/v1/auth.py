from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.database import get_session
from app.models.user import User, UserCreate, UserResponse, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_user, get_admin_user


router = APIRouter(prefix="/auth", tags=["Autenticación"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, session: Session = Depends(get_session)):
    """Registra un nuevo usuario con rol SELLER."""
    if session.exec(select(User).where(User.email == user_data.email)).first():
        raise HTTPException(status_code=400, detail="El email ya existe")

    new_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role="SELLER",
        hashed_password=get_password_hash(user_data.password),
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """Verifica credenciales y devuelve un token JWT."""
    user = session.exec(select(User).where(User.email == form_data.username)).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/create-admin", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_another_admin(
    user_data: UserCreate,
    admin: User = Depends(get_admin_user),
    session: Session = Depends(get_session),
):
    """Solo un ADMIN puede crear otros ADMINs."""
    if session.exec(select(User).where(User.email == user_data.email)).first():
        raise HTTPException(status_code=400, detail="El email ya existe")

    new_admin = User(
        email=user_data.email,
        full_name=user_data.full_name,
        role="ADMIN",
        hashed_password=get_password_hash(user_data.password),
    )
    session.add(new_admin)
    session.commit()
    session.refresh(new_admin)
    return new_admin


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Devuelve el perfil del usuario autenticado."""
    return current_user