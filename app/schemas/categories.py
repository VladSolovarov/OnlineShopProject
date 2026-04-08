from typing import Annotated

from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    """Uses to create and update categories. (PUT, POST)"""
    name: Annotated[str, Field(
        min_length=2,
        max_length=50,
        description="Category name (2-50 symbols)"
    )]

    parent_id: Annotated[int | None, Field(
        default=None,
        description="Parent category ID"
    )]


class Category(BaseModel):
    """Get category data. (GET)"""
    id: Annotated[int, Field(
        description="Unique category ID"
    )]

    name: Annotated[str, Field(
        description="Category name"
    )]

    parent_id: Annotated[int | None, Field(
        default=None,
        description="Parent category ID"
    )]

    is_active: Annotated[bool, Field(
        description="Is active category"
    )]

    model_config=ConfigDict(from_attributes=True)
