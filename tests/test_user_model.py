from sqlalchemy import create_engine, inspect

from app.db.base import Base
from app.models.user import User


def test_user_table_can_be_created() -> None:
    engine = create_engine("sqlite:///:memory:")

    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    assert User.__tablename__ in table_names

    column_names = {
        column["name"]
        for column in inspector.get_columns("users")
    }

    assert column_names == {
        "id",
        "email",
        "nickname",
        "password_hash",
        "created_at",
    }