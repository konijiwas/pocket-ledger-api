from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.category import Category
from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import (
    TransactionCreate,
    TransactionRead,
    TransactionUpdate,
)

router = APIRouter(
    prefix="/transactions",
    tags=["流水"],
)


@router.post(
    "",
    response_model=TransactionRead,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Transaction:
    category = db.scalar(
        select(Category).where(
            Category.id == transaction_data.category_id,
            Category.user_id == current_user.id,
        )
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CATEGORY_NOT_FOUND",
                "message": "分类不存在",
            },
        )

    if category.type != transaction_data.type.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "TRANSACTION_TYPE_MISMATCH",
                "message": "流水类型必须和分类类型一致",
            },
        )

    transaction = Transaction(
        amount=transaction_data.amount,
        type=transaction_data.type.value,
        occurred_on=transaction_data.occurred_on,
        note=transaction_data.note,
        category_id=transaction_data.category_id,
        user_id=current_user.id,
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction


@router.get(
    "",
    response_model=list[TransactionRead],
)
def list_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Transaction]:
    transactions = db.scalars(
        select(Transaction)
        .where(
            Transaction.user_id == current_user.id,
        )
        .order_by(
            Transaction.occurred_on.desc(),
            Transaction.id.desc(),
        )
    ).all()

    return list(transactions)


@router.patch(
    "/{transaction_id}",
    response_model=TransactionRead,
)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Transaction:
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "TRANSACTION_NOT_FOUND",
                "message": "流水不存在",
            },
        )

    update_data = transaction_data.model_dump(
        exclude_unset=True,
    )

    category = db.scalar(
        select(Category).where(
            Category.id == update_data.get(
                "category_id",
                transaction.category_id,
            ),
            Category.user_id == current_user.id,
        )
    )

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "CATEGORY_NOT_FOUND",
                "message": "分类不存在",
            },
        )

    updated_type = update_data.get(
        "type",
        transaction.type,
    )

    if hasattr(updated_type, "value"):
        updated_type = updated_type.value

    if category.type != updated_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "TRANSACTION_TYPE_MISMATCH",
                "message": "流水类型必须和分类类型一致",
            },
        )

    if "type" in update_data:
        transaction.type = updated_type

    if "amount" in update_data:
        transaction.amount = update_data["amount"]

    if "occurred_on" in update_data:
        transaction.occurred_on = update_data["occurred_on"]

    if "note" in update_data:
        transaction.note = update_data["note"]

    if "category_id" in update_data:
        transaction.category_id = update_data["category_id"]

    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete(
    "/{transaction_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "TRANSACTION_NOT_FOUND",
                "message": "流水不存在",
            },
        )

    db.delete(transaction)
    db.commit()