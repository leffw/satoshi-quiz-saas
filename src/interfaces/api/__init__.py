from src.interfaces.api.middlewares.authentication import isAuthentication
from src.interfaces.api.routes import setup, quiz, reward
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.configs import API_HOST, API_PORT
from fastapi import FastAPI, Depends

import uvicorn

api = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    swagger_ui_oauth2_redirect_url=None,
    dependencies=[Depends(isAuthentication)],
)
api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(reward.router)
api.include_router(setup.router)
api.include_router(quiz.router)

@api.get("/health/liveness")
async def health_liveness():
    return JSONResponse({"liveness": True})

@api.get("/health/readiness")
async def health_readiness():
    readiness = True
    return JSONResponse({"readiness": readiness}, status_code=(200 if (readiness) else 503))

def start():
    uvicorn.run(api, host=API_HOST, port=API_PORT, loop="asyncio", log_config={
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "foo-logger": {"handlers": ["default"], "level": "DEBUG"},
        },
    })