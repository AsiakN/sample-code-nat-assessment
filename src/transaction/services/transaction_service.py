import json
from typing import List

from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import parse_obj_as
from src.transaction.Exceptions.exceptions import TransactionRecordNotFoundError
from src.transaction.db.repository import TransactionRepository
from src.transaction.dto.requests.transaction_create_req import TransactionCreateRequest, TransactionUpdateRequest
from src.transaction.dto.responses.http_response import TransactionCreateResponse
from fastapi import Request


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
        @param transaction_id:
        @return: transaction payload
        """
        response = await self._repository.delete_transaction(transaction_id)
        if response.deleted_count == 1:
            return True

        raise TransactionRecordNotFoundError(transaction_id)

    async def fetch_transaction_history(self, user_id: str, request: Request) -> List[TransactionCreateResponse]:
        """
        Get list of transactions for a user
        @param user_id:  id
        @param request
        @return:  list of transactions by a user
        """
        cache_key = f"{user_id}:transaction_history"

        # Check if the result is cached
        cached_result = await self.get_cache(cache_key, request)
        if cached_result:
            return cached_result

        records = await self._repository.fetch_user_transaction_history(user_id)
        mapped_response = parse_obj_as(List[TransactionCreateResponse], records)
        logger.info(mapped_response)
        if records:
            # Convert the Pydantic objects into JSON serializable data
            encoded_response = jsonable_encoder(mapped_response)

            # Serialize the encoded response into a JSON string
            serialized_response = json.dumps(encoded_response)
            await self.set_cache(cache_key, request, serialized_response)

        return mapped_response

    async def fetch_transaction_analytics(self, user_id: str, request: Request):
        """
        Get summary of transaction data for a user
        @param user_id: 's id
        @return:  list of transactions by a user
        @param request:
        """
        cache_key = f"{user_id}:transaction_analytics"
        cached_result = await self.get_cache(cache_key, request)
        if cached_result:
            return cached_result

        records = await self._repository.fetch_user_transaction_analytics(user_id=user_id)
        if records:
            await self.set_cache(cache_key, request, records)

        return records

    async def get_cache(self, key: str, request):
        redis_service = request.app.state.redis_service

        # Check if the result is cached
        cached_result = await redis_service.get_cache(key)
        return cached_result

    async def set_cache(self, key, request, records):
        redis_service = request.app.state.redis_service
        await redis_service.set_cache(records, key)
