from fastapi import FastAPI
from app.api.routes import router
from app.db.database import Base, engine

app = FastAPI(title="Assembly Parts Inventory")

# Creates tables automatically for local/dev
Base.metadata.create_all(bind=engine)

app.include_router(router)