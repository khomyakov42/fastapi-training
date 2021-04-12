from fastapi import APIRouter, Response
from fastapi.exceptions import HTTPException

from exceptions import ObjectNotFound
from .models import Account, InsufficientFunds
from . import schemas, models

router = APIRouter()


@router.post("/accounts/{account_id}/deposit", status_code=204, response_class=Response)
async def deposit_to_account(account_id: int, body: schemas.DepositAccountRequest):
    account = await Account.get(account_id)
    if account is None:
        raise ObjectNotFound(model="account", identifier=account_id)
    await account.change_balance(body.amount)


@router.post("/accounts/{account_id}/transfer", status_code=204, response_class=Response)
async def transfer_to_account(account_id: int, body: schemas.TransferAccountRequest):
    account1 = await Account.get(account_id)
    if account1 is None:
        raise ObjectNotFound(model="account", identifier=account_id)

    account2 = await Account.get(body.account_id)
    if account2 is None:
        raise ObjectNotFound(model="account", identifier=body.account_id)

    await account1.transfer(account2, body.amount)

