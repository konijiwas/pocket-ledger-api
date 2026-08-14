from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.models.category import Category


def test_category_table_can_be_created() -> None:
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    inspector = inspect(engine)

    assert Category.__tablename__ in inspector.get_table_names()

    column_names = {
        column["name"]
        for column in inspector.get_columns("categories")
    }

    assert column_names == {
        "id",
        "name",
        "type",
        "user_id",
        "created_at",
    }

    foreign_keys = inspector.get_foreign_keys(
        "categories"
    )

    assert any(
        foreign_key["constrained_columns"] == ["user_id"]
        and foreign_key["referred_table"] == "users"
        for foreign_key in foreign_keys
    )

    unique_constraints = inspector.get_unique_constraints(
        "categories"
    )

    assert any(
        set(constraint["column_names"])
        == {"user_id", "name", "type"}
        for constraint in unique_constraints
    )