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
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryRead,
    CategoryUpdate,
)


router = APIRouter(
    prefix="/categories",
    tags=["分类"],
)


@router.post(
    "",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Category:
    existing_category = db.scalar(
        select(Category).where(
            Category.user_id == current_user.id,
            Category.name == category_data.name,
            Category.type == category_data.type.value,
        )
    )

    if existing_category is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CATEGORY_ALREADY_EXISTS",
                "message": "该分类已经存在",
            },
        )

    category = Category(
        name=category_data.name,
        type=category_data.type.value,
        user_id=current_user.id,
    )

    db.add(category)
    db.commit()
    db.refresh(category)

    return category


@router.get(
    "",
    response_model=list[CategoryRead],
)
def list_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Category]:
    categories = db.scalars(
        select(Category)
        .where(
            Category.user_id == current_user.id
        )
        .order_by(
            Category.type,
            Category.name,
        )
    ).all()

    return list(categories)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Category:
    category = db.scalar(
        select(Category).where(
            Category.id == category_id,
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

    updated_name = (
        category_data.name
        if category_data.name is not None
        else category.name
    )
    updated_type = (
        category_data.type.value
        if category_data.type is not None
        else category.type
    )

    duplicate_category = db.scalar(
        select(Category).where(
            Category.user_id == current_user.id,
            Category.name == updated_name,
            Category.type == updated_type,
            Category.id != category.id,
        )
    )

    if duplicate_category is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "CATEGORY_ALREADY_EXISTS",
                "message": "该分类已经存在",
            },
        )

    category.name = updated_name
    category.type = updated_type

    db.commit()
    db.refresh(category)

    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    category = db.scalar(
        select(Category).where(
            Category.id == category_id,
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

    db.delete(category)
    db.commit()