from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, Field


class Review(BaseModel):
    id: Annotated[int, Field(
        description="Unique review ID"
    )]

    user_id: Annotated[int, Field(
        description="User ID of review"
    )]

    product_id: Annotated[int, Field(
        description="Product ID of review"
    )]

    comment: Annotated[str | None, Field(
        max_length=1000,
        default=None,
        description="Review text",
    )]

    comment_date: Annotated[datetime, Field(
        default_factory=datetime.now,
        description="Review datetime"
    )]

    grade: Annotated[int, Field(
        ge=1,
        le=5,
        description="Review grade"
    )]

    is_active: Annotated[bool, Field(
        description="Is the active status of review"
    )]


class ReviewCreate(BaseModel):
    product_id: Annotated[int, Field(
        description="Product id of this review"
    )]

    comment: Annotated[str | None, Field(
        default=None,
        description="Review text (up to 1000 symbols)"
    )]

    grade: Annotated[int, Field(
        ge=1,
        le=5,
        description="Review grade (from 1 to 5)"
    )]
