import decimal

from db import db
from sqlalchemy.sql import func

from exceptions import LogicError


class InsufficientFunds(LogicError):
    error_code = "insufficient_funds"

    def __init__(self, account_id: int, balance: decimal.Decimal):
        super(InsufficientFunds, self).__init__(
            error=f"Insufficient funds on the account {account_id}",
            detail={
                "account_id": account_id,
                "balance": str(balance),
            }
        )


class Account(db.Model):
    __tablename__ = "accounts"

    id = db.Column(db.BigInteger(), primary_key=True)
    balance = db.Column(db.Numeric(precision=20, scale=2), nullable=False, default=0)

    async def change_balance(self, change: decimal.Decimal):
        async with db.transaction():
            balance = await Account.select("balance").where(Account.id == self.id).with_for_update().gino.scalar()
            new_balance = balance + change
            if new_balance < 0:
                raise InsufficientFunds(account_id=self.id, balance=balance)

            await Transaction.create(
                account_id=self.id,
                amount=change,
            )
            await self.update(balance=new_balance).apply()

    async def transfer(self, account: 'Account', amount: decimal.Decimal):
        assert amount > 0
        async with db.transaction():
            # preventing dead lock
            account_ids = sorted([self.id, account.id])
            await Account.select("balance").where(
                Account.id.in_(account_ids)
            ).with_for_update().gino.all()

            await self.change_balance(-amount)
            await account.change_balance(amount)


class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.BigInteger(), primary_key=True)
    amount = db.Column(db.Numeric(precision=20, scale=2), nullable=False)
    account_id = db.Column(db.BigInteger(), db.ForeignKey("accounts.id"), nullable=False)
    created_at = db.Column(db.DateTime(), server_default=func.now(), nullable=False)


async def create_account() -> Account:
    return await Account.create()

