from datetime import datetime
from typing import Optional

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException, Request
from loguru import logger

from src.bootstrap.containers import Container
from src.transaction.Exceptions.exceptions import TransactionRecordNotFoundError
from src.transaction.dto.requests.transaction_create_req import TransactionCreateRequest, TransactionUpdateRequest
from src.transaction.dto.responses.http_response import TransactionCreateResponse, PagedHttpResponseModel, \
    SingleDataResponseModel
from src.transaction.services.transaction_service import TransactionService

router = APIRouter()


@router.post("/api/v1/transactions", tags=["Transactions"], response_model=SingleDataResponseModel, status_code=201)
@inject
async def create_transaction_request(
        payload: TransactionCreateRequest,
        transaction_service: TransactionService = Depends(Provide[Container.transaction_service])):
    """
    Endpoint to create a transaction record
    """
    try:
        response = await transaction_service.create_transaction(payload)
        return SingleDataResponseModel(is_successful=True,
                                       message="Transaction created successfully",
                                       data=response.dict())
    except Exception as e:
        raise HTTPException(status_code=500, detail=e)


@router.put("/api/v1/transactions/{transaction_id}", tags=["Transactions"], response_model=SingleDataResponseModel)
@inject
async def update_transaction_details(
        transaction_id: str,
        payload: TransactionUpdateRequest,
        transaction_service: TransactionService = Depends(Provide[Container.transaction_service])):
    """
    Endpoint to edit a transaction
    """

    try:
        response = await transaction_service.update_transaction(transaction_id, payload)
        return SingleDataResponseModel(is_successful=True,
                                       message="Transaction updated successfully",
                                       data=response.dict())

    except TransactionRecordNotFoundError:
        raise HTTPException(status_code=404, detail="Transaction not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail="Sorry! Something went wrong.")


@router.delete("/api/v1/transactions/{transaction_id}", tags=["Transactions"], status_code=204)
@inject
async def delete_finance_request(
        transaction_id: str,
        transaction_service: TransactionService = Depends(Provide[Container.transaction_service])):
    """
    Endpoint to delete transaction record
    """
    try:
        response = await transaction_service.delete_transaction(transaction_id)
        return response
    except TransactionRecordNotFoundError:
        raise HTTPException(status_code=404, detail="Transaction record not found")


@router.get("/api/v1/transactions/{user_id}", tags=["Transactions"], response_model=PagedHttpResponseModel)
@inject
async def get_transaction_history(
        user_id: str,
        request: Request,
        page: int = 1,
        page_size: int = 10,
        transaction_service: TransactionService = Depends(Provide[Container.transaction_service])):
    """
    Endpoint to retrieve transaction history for a user
    """

    response = await transaction_service.fetch_transaction_history(user_id, request)

    return PagedHttpResponseModel(is_successful=True,
                                  message="operation completed successfully",
                                  page=page,
                                  page_size=len(response),
                                  data=response)


@router.get("/api/v1/transactions/{user_id}/analytics", tags=["Transactions"])
@inject
async def get_transaction_analytics(user_id: str,
                                    request: Request,
                                    start_date:  Optional[datetime] = None,
                                    end_date: Optional[datetime] = None,
                                    transaction_service: TransactionService = Depends(
                                        Provide[Container.transaction_service])
                                    ):
    """
    Endpoint to retrieve transaction analytics for a user
    @Query params = start_date
    @Query params = end_date
    """
    response = await transaction_service.fetch_transaction_analytics(user_id, request)
    logger.info(response)
    return SingleDataResponseModel(is_successful=True,
                                   message="Successfully retrieved stats",
                                   data=response
                                   )
