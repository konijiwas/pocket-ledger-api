from decimal import Decimal

from pydantic import BaseModel


class SummaryRead(BaseModel):
    income_total: Decimal
    expense_total: Decimal
    balance: Decimal