import uvicorn
from fastapi import FastAPI, Request, status
from src.conf import messages
from src.api import contacts, utils, auth, users
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from src.services.redis_cache import redis_cache
from src.services.auth import Hash


app = FastAPI()
origins = [
    "*",
]

hashed_pwd = Hash.hash_password("password123")


@app.on_event("startup")
async def startup():
    await redis_cache.connect()


@app.on_event("shutdown")
async def shutdown():
    await redis_cache.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(utils.router, prefix="/api")
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"error": "Перевищено ліміт запитів. Спробуйте пізніше."},
    )


@app.get("/")
async def root():
    return {"message": messages.WELCOME_MESSAGE}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, workers=4)
