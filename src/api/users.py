from fastapi import APIRouter, Depends, Request
from src.services.limiter import limiter
from src.schemas.users import User
from src.services.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=User)
@limiter.limit("10/minute")
async def me(request: Request, user: User = Depends(get_current_user)):
    return user
