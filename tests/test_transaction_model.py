from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.models.transaction import Transaction


def test_transaction_table_can_be_created() -> None:
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    inspector = inspect(engine)

    assert Transaction.__tablename__ in inspector.get_table_names()

    column_names = {
        column["name"]
        for column in inspector.get_columns("transactions")
    }

    assert column_names == {
        "id",
        "amount",
        "type",
        "occurred_on",
        "note",
        "category_id",
        "user_id",
        "created_at",
        "updated_at",
    }

    foreign_keys = inspector.get_foreign_keys(
        "transactions"
    )

    referenced_tables = {
        foreign_key["referred_table"]
        for foreign_key in foreign_keys
    }

    assert referenced_tables == {
        "categories",
        "users",
    }