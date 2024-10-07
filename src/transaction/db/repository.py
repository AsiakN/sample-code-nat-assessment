from bson import ObjectId
from loguru import logger
from pymongo.asynchronous.collection import ReturnDocument

from src.persistence.base import transaction_collection


class TransactionRepository:
    """
        Repository to deal with data access to transactions table
    """

    async def create_transaction(self, transaction_data: dict) -> dict:
        """
               Saves invoice payload

               @param transaction_data: params transaction data
               @return: dict
        """
        transaction = await transaction_collection.insert_one(transaction_data)
        new_transaction = await transaction_collection.find_one({"_id": transaction.inserted_id})
        return new_transaction

    async def update_transaction(self, transaction_id: str, transaction_data: dict):
        """
        Update individual fields of an existing transaction record.

        Only the provided fields will be updated.
        Any missing or `null` fields will be ignored.
        """
        update_transaction = await transaction_collection.find_one_and_update(
            {"_id": ObjectId(transaction_id)},
            {"$set": transaction_data},
            return_document=ReturnDocument.AFTER,
        )
        return update_transaction

    async def delete_transaction(self, transaction_id: str):
        """
        Remove a single transaction record from the database.
        """
        delete_result = await transaction_collection.delete_one({"_id": ObjectId(transaction_id)})

        return delete_result

    async def fetch_user_transaction_history(self, user_id: str):
        """
        Get the transaction history for a specific user, by `user_id`.
        :param user_id:
        :return:
        """
        transactions = []
        cursor = transaction_collection.find({"user_id": user_id}).sort({"transaction_date": -1})

        for document in await cursor.to_list(length=100):
            transactions.append(document)

        return transactions

    async def fetch_user_transaction_analytics(self, user_id: str):
        """
        Assuming a single currency to allow for simplicity

        Get the transaction history for a specific user, by `user_id`.
        :param user_id:
        :return:
        """
        pipeline = [
            # Match transactions for the given user_id
            {"$match": {"user_id": user_id}},

            # Group by day (use transaction_date for day grouping and sum the transaction amounts)
            {"$group": {
                "_id": {
                    "day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$transaction_date"}}
                },
                "total_transactions_per_day": {"$sum": 1},
                "total_amount_per_day": {"$sum": "$transaction_amount"}
            }},

            # Calculate the average transaction value for each day
            {"$group": {
                "_id": None,  # Remove grouping by day for the overall average
                "total_amount": {"$sum": "$total_amount_per_day"},  # Sum all transaction amounts
                "total_transactions": {"$sum": "$total_transactions_per_day"},  # Count all transactions
                "days_with_transactions": {"$push": {
                    "day": "$_id.day",
                    "transaction_count": "$total_transactions_per_day"
                }}
            }},

            {"$project": {
                "_id": 0,
                "average_transaction_value": {
                    "$cond": {
                        "if": {"$eq": ["$total_transactions", 0]},  # Prevent division by zero
                        "then": 0,
                        "else": {"$divide": ["$total_amount", "$total_transactions"]}  # Calculate the average
                    }
                },
                "days_with_transactions": 1  # Pass the days array for sorting in the next step
            }},

            # Sort by transaction count and get the day with the highest transaction count
            {"$unwind": "$days_with_transactions"},
            {"$sort": {"days_with_transactions.transaction_count": -1}},
            {"$limit": 1},

            # Format the final output
            {"$project": {
                "_id": 0,
                "average_transaction_value": 1,
                "day_with_most_transactions": "$days_with_transactions.day",
                "transaction_count_on_that_day": "$days_with_transactions.transaction_count"
            }}
        ]
        result = transaction_collection.aggregate(pipeline)

        result = await result.to_list()

        if result:
            return result[0]
        return None
