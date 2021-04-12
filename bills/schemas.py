from pydantic import BaseModel, condecimal, conint


class DepositAccountRequest(BaseModel):
    amount: condecimal(gt=0, decimal_places=2)


class TransferAccountRequest(BaseModel):
    account_id: conint(gt=0)
    amount: condecimal(gt=0, decimal_places=2)


class Account(BaseModel):
    id: conint(gt=0)
    balance: condecimal(decimal_places=2)

    class Config:
        orm_mode = True
