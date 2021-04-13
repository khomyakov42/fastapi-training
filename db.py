import os
from gino.ext.starlette import Gino

DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
DATABASE_PORT = int(os.getenv("DATABASE_PORT", "5432"))


db = Gino(
    dsn=f"postgresql://postgres:postgres@{DATABASE_HOST}:{DATABASE_PORT}/postgres",
)
