from datetime import datetime
from pydantic import BaseConfig, BaseModel, condecimal, constr, validator, ConfigDict, field_validator, root_validator, \
    model_validator

from src.transaction.utils.security import encrypt_field


class TransactionTypeConstants:
    DEBIT: str = "debit"
    CREDIT: str = "credit"


def convert_datetime_to_realworld(dt: datetime) -> str:
    return dt.replace(tzinfo=None).isoformat().replace("+00:00", "Z")


class RWModel(BaseModel):
    class Config:
        ConfigDict(
            populate_by_name=True,
            json_encoders={datetime: convert_datetime_to_realworld},
            arbitrary_types_allowed=True,
            json_schema_extra={
                "example": {
                    "user_id": "e7tyewrkjtty",
                    "full_name": "Jane Doe",
                    "transaction_amount": 475.66,
                    "transaction_type": "credit",
                    "transaction_date": "2024-10-05T09:40:53.695Z",
                    "transaction_currency": "USD"
                }
            })


class TransactionCreateRequest(RWModel):
    user_id: str
    full_name: str
    transaction_amount: condecimal(gt=0)
    transaction_type: constr(strip_whitespace=True)
    transaction_date: datetime
    transaction_currency: str

    @field_validator('transaction_type')
    def validate_transaction_type(cls, transaction_type: str):
        valid_types = [TransactionTypeConstants.DEBIT, TransactionTypeConstants.CREDIT]

        if transaction_type is None:
            return transaction_type
        elif transaction_type not in valid_types:
            raise ValueError(f"value must be one of: {valid_types}")
        return transaction_type

    @model_validator(mode='before')
    def encrypt_sensitive_data(cls, values):
        # Encrypt user_id and full_name
        if "full_name" in values:
            values["full_name"] = encrypt_field(values["full_name"])
        return values


class TransactionUpdateRequest(RWModel):
    full_name: str
    transaction_amount: condecimal(gt=0)
    transaction_type: constr(strip_whitespace=True)
    transaction_date: datetime
    transaction_currency: str

    @field_validator('transaction_type')
    def validate_transaction_type(cls, transaction_type: str):
        valid_types = [TransactionTypeConstants.DEBIT, TransactionTypeConstants.CREDIT]

        if transaction_type is None:
            return transaction_type
        elif transaction_type not in valid_types:
            raise ValueError(f"value must be one of: {valid_types}")
        return transaction_type

    @model_validator(mode='before')
    def encrypt_sensitive_data(cls, values):
        # Encrypt user_id and full_name
        if "full_name" in values:
            values["full_name"] = encrypt_field(values["full_name"])
        return values
