from fastapi import APIRouter
from .schemas import CreateCustomerRequest, Customer
from .models import create_customer

router = APIRouter()


@router.post("/customers/", response_model=Customer, status_code=201)
async def create_customer_api(body: CreateCustomerRequest):
    customer = await create_customer(
        name=body.name
    )

    return customer
