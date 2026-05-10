import os
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

import bases.__init__ # needs this to init all models before init backend

from auth.routes import router as auth_router
from users.routes import router as users_router

load_dotenv()

API_VERSION = os.getenv("API_VERSION")
API_PREFIX_WITH_VERSION = f"/api/v{API_VERSION}"
ORIGIN = os.getenv("ORIGIN")

origins = [
    ORIGIN
]

app = FastAPI(title="VNCubing API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix=API_PREFIX_WITH_VERSION)

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(users_router, prefix="/users", tags=["users"])

@app.get("/", response_class=HTMLResponse)
def root():
    return f"""
    <html>
        <head>
            <title>VNCubing Backend Status</title>
        </head>
        <body>
            <p>VNCubing API v{API_VERSION} is up and ready.</p>
        </body>
    </html>
    """

@api_router.get("/health")
def health():
    return {"status": "ok"}

app.include_router(api_router)