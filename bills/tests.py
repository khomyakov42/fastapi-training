import asyncio
from unittest import TestCase
from fastapi.testclient import TestClient

from bills.models import Account, Transaction


def sync_exec(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


class BillsTestCase(TestCase):
    def setUp(self) -> None:
        from main import app
        self.client = TestClient(app)
        self.client.__enter__()
        self.account = sync_exec(Account.create())
        self.account2 = sync_exec(Account.create())

    def tearDown(self):
        self.client.__exit__()

    def deposit_to_account(self, account_id, amount):
        return self.client.post(f"/accounts/{account_id}/deposit", json={
            "amount": str(amount)
        })

    def transfer_to_account(self, account_from_id, account_to_id, amount):
        return self.client.post(f"/accounts/{account_from_id}/transfer", json={
            "amount": str(amount),
            "account_id": account_to_id
        })

    def test_new_account_with_zero_balance(self):
        """Новый счет имеет нулевой баланс и не имеет транзакций"""

        self.assertEqual(0, self.account.balance)
        txs = sync_exec(Transaction.query.where(Transaction.account_id == self.account.id).gino.all())
        self.assertEqual(0, len(txs))

    def test_deposit_to_account(self):
        """Пополнение счета"""

        resp = self.deposit_to_account(account_id=self.account.id, amount=100)
        self.assertEqual(204, resp.status_code)

        self.account = sync_exec(Account.get(self.account.id))

        self.assertEqual(100, self.account.balance)
        txs = sync_exec(Transaction.query.where(Transaction.account_id == self.account.id).gino.all())
        self.assertEqual(1, len(txs))

        self.assertEqual(100, txs[0].amount)

    def test_deposit_to_not_exists_account(self):
        """Пополнение не существующего счета"""

        account_id = 2 ** 32
        resp = self.deposit_to_account(account_id=account_id, amount=100)
        self.assertEqual(404, resp.status_code)
        data = resp.json()
        self.assertEqual("not_found", data["error_code"])
        self.assertEqual("account", data["detail"]["model"])
        self.assertEqual(account_id, data["detail"]["identifier"])

    def test_deposit_to_account_with_negative_amount(self):
        """Пополнение счета на отрицательную сумму"""

        resp = self.deposit_to_account(account_id=self.account.id, amount=-100)
        self.assertEqual(400, resp.status_code)

    def test_transfer_to_account(self):
        """Перевод средств с одного счета на другой"""

        sync_exec(self.account.change_balance(100))
        deposit_tx = sync_exec(Transaction.query.where(Transaction.account_id == self.account.id).gino.first())

        resp = self.transfer_to_account(account_from_id=self.account.id, account_to_id=self.account2.id, amount=100)
        self.assertEqual(204, resp.status_code)

        self.account = sync_exec(Account.get(self.account.id))
        self.assertEqual(0, self.account.balance)

        self.account2 = sync_exec(Account.get(self.account2.id))
        self.assertEqual(100, self.account2.balance)

        from_txs = sync_exec(Transaction.query.where(
            (Transaction.account_id == self.account.id) & (Transaction.id != deposit_tx.id)
        ).gino.all())
        self.assertEqual(1, len(from_txs))
        self.assertEqual(-100, from_txs[0].amount)

        to_txs = sync_exec(Transaction.query.where(Transaction.account_id == self.account2.id).gino.all())
        self.assertEqual(1, len(to_txs))
        self.assertEqual(100, to_txs[0].amount)

        self.assertEqual(from_txs[0].created_at, to_txs[0].created_at)

    def test_transfer_to_account_with_zero_balance(self):
        """Перевод суммы большей, чем есть на балансе"""

        resp = self.transfer_to_account(account_from_id=self.account.id, account_to_id=self.account2.id, amount=100)
        self.assertEqual(422, resp.status_code)
        data = resp.json()
        self.assertEqual("insufficient_funds", data["error_code"])

    def test_transfer_from_not_exists_account(self):
        """Перевод средств с не существующего счета"""

        account_from_id = 2 ** 32
        resp = self.transfer_to_account(account_from_id=account_from_id, account_to_id=self.account2.id, amount=100)
        self.assertEqual(404, resp.status_code)
        data = resp.json()
        self.assertEqual("not_found", data["error_code"])
        self.assertEqual("account", data["detail"]["model"], "account")
        self.assertEqual(account_from_id, data["detail"]["identifier"])

    def test_transfer_to_not_exists_account(self):
        """Перевод средств на не существующий счет"""

        account_to_id = 2 ** 32
        resp = self.transfer_to_account(account_from_id=self.account.id, account_to_id=account_to_id, amount=100)
        self.assertEqual(404, resp.status_code)
        data = resp.json()
        self.assertEqual("not_found", data["error_code"])
        self.assertEqual("account", data["detail"]["model"], "account")
        self.assertEqual(account_to_id, data["detail"]["identifier"])
