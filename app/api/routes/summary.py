from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.summary import SummaryRead


router = APIRouter(
    prefix="/summary",
    tags=["统计"],
)


@router.get(
    "",
    response_model=SummaryRead,
)
def read_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SummaryRead:
    income_total, expense_total = db.execute(
        select(
            func.coalesce(
                func.sum(
                    case(
                        (
                            Transaction.type == "income",
                            Transaction.amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
            func.coalesce(
                func.sum(
                    case(
                        (
                            Transaction.type == "expense",
                            Transaction.amount,
                        ),
                        else_=0,
                    )
                ),
                0,
            ),
        ).where(
            Transaction.user_id == current_user.id,
        )
    ).one()

    income_total = Decimal(str(income_total))
    expense_total = Decimal(str(expense_total))

    return SummaryRead(
        income_total=income_total,
        expense_total=expense_total,
        balance=income_total - expense_total,
    )
