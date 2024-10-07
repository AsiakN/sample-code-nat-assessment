from dependency_injector import containers, providers

from src.transaction.services.transaction_service import TransactionService
from src.transaction.db.repository import TransactionRepository


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    transaction_repository = providers.Factory(
        TransactionRepository
    )
    transaction_service = providers.Factory(
        TransactionService,
        transaction_repository=transaction_repository,
    )

    redis_service = providers.Factory(

    )
