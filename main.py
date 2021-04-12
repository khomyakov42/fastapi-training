from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST
from db import db


from customers.views import router as customers_router
from bills.views import router as billing_router
from exceptions import LogicError, ObjectNotFound

app = FastAPI()

db.init_app(app)
app.include_router(customers_router)
app.include_router(billing_router)


@app.on_event("startup")
async def startup_event():
    await db.gino.create_all()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=HTTP_400_BAD_REQUEST,
        content={"detail": jsonable_encoder(exc.errors())},
    )


@app.exception_handler(LogicError)
async def logic_exception_handler(request, exc: LogicError):
    error_code = exc.error_code
    status_code = 422
    error = exc.error
    detail = exc.detail
    if isinstance(exc, ObjectNotFound):
        status_code = 404

    return JSONResponse(
        status_code=status_code,
        content={
            "error_code": error_code,
            "error": error,
            "detail": detail
        }
    )
