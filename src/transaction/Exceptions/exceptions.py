class NotFoundError(Exception):
    entity_name: str

    def __init__(self, entity_id):
        super().__init__(f"{self.entity_name} not found, id: {entity_id}")


class TransactionRecordNotFoundError(NotFoundError):
    entity_name: str = "transactions"
