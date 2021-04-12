from pydantic import BaseModel, constr
from bills.schemas import Account


class CreateCustomerRequest(BaseModel):
    name: constr(min_length=1, max_length=64)


class Customer(BaseModel):
    id: int
    name: str
    account: Account

    class Config:
        orm_mode = True
