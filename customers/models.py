from db import db
from bills.models import create_account, Account


class Customer(db.Model):
    __tablename__ = "customers"
    __table_args__ = (
        db.UniqueConstraint('id', 'account_id', name='unique_account'),
    )

    id = db.Column(db.BigInteger(), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    account_id = db.Column(db.BigInteger(), db.ForeignKey("accounts.id"), nullable=False)
    _account = None

    @property
    def account(self) -> Account:
        assert self._account is not None, "Load account using query"
        return self._account


async def create_customer(name: str) -> Customer:
    async with db.transaction():
        account = await create_account()
        customer = await Customer.create(name=name, account_id=account.id)
        customer._account = account
        return customer
