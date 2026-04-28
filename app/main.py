from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(title="Country Information AI Agent")

app.include_router(router)