from __future__ import annotations

from src.ui.pages.transactions_page import TransactionsPage


class TransactionFlow:
    def __init__(self, transactions_page: TransactionsPage) -> None:
        self.transactions_page = transactions_page

