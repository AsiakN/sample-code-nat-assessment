from __future__ import annotations

from datetime import datetime
from typing import List, Any, Optional, Annotated

from pydantic import BaseModel, BeforeValidator, Field, ConfigDict, model_validator

from src.transaction.dto.requests.transaction_create_req import convert_datetime_to_realworld, RWModel
from src.transaction.utils.security import decrypt_field


class HttpResponseModel(BaseModel):
    is_successful: bool
    message: str


class SingleDataResponseModel(HttpResponseModel):
    data: Optional[Any]


class PagedHttpResponseModel(HttpResponseModel):
    page: int = 1
    page_size: int
    # total: int
    data: List


PyObjectId = Annotated[str, BeforeValidator(str)]


class TransactionCreateResponse(RWModel):
    user_id: str
    transaction_currency: str
    transaction_type: str
    transaction_amount: float
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    full_name: str
    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={datetime: convert_datetime_to_realworld},
    )

    @model_validator(mode='before')
    def decrypt_sensitive_data(cls, values):
        # Decrypt full_name
        if "full_name" in values:
            values["full_name"] = decrypt_field(values["full_name"])

        return values
