from typing import List

from loguru import logger

from pydantic import parse_obj_as

from src.transaction.Exceptions.exceptions import TransactionRecordNotFoundError
from src.transaction.db.repository import TransactionRepository
from src.transaction.dto.requests.transaction_create_req import TransactionCreateRequest, TransactionUpdateRequest
from src.transaction.dto.responses.http_response import TransactionCreateResponse


class TransactionService:

    def __init__(self, transaction_repository: TransactionRepository) -> None:
        self._repository = transaction_repository

    async def create_transaction(self, payload: TransactionCreateRequest) -> TransactionCreateResponse:
        """
        create a transaction record
        @param payload
        @return: transaction payload
        """
        created = await self._repository.create_transaction(payload.dict())
        if created:
            transaction_response = TransactionCreateResponse(**created)
            return transaction_response

    async def update_transaction(self, transaction_id: str,
                                 payload: TransactionUpdateRequest) -> TransactionCreateResponse:
        """
        create a transaction record
        @param payload
        @param transaction_id:
        @return: transaction payload
        """
        response = await self._repository.update_transaction(transaction_id, payload.dict())

        if response is not None:
            return TransactionCreateResponse(**response)
        else:
            raise TransactionRecordNotFoundError(transaction_id)

    async def delete_transaction(self, transaction_id: str) -> bool:
        """
        delete a transaction record
        @return: transaction payload
        :param transaction_id:
        """
        response = await self._repository.delete_transaction(transaction_id)
        if response.deleted_count == 1:
            return True

        raise TransactionRecordNotFoundError(transaction_id)

    async def fetch_transaction_history(self, identifier: str) -> List[TransactionCreateResponse]:
        """
        Get list of transactions for a user
        @param identifier:  id
        @return:  list of transactions by a user
        """
        records = await self._repository.fetch_user_transaction_history(identifier)
        mapped_response = parse_obj_as(List[TransactionCreateResponse], records)
        return mapped_response

    async def fetch_transaction_analytics(self, identifier: str):
        """
        Get summary of transaction data for a user
        @param identifier: user's id
        @return:  list of transactions by a user
        """
        records = await self._repository.fetch_user_transaction_analytics(identifier)
        return records
