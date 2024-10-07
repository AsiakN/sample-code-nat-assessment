import os
import motor.motor_asyncio
from dotenv import load_dotenv
from bson.codec_options import CodecOptions
from .custom_type import type_registry
# from config import Config
load_dotenv()

codec_options = CodecOptions(type_registry=type_registry)

MONGODB_URL = os.getenv("MONGODB_URL")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
db = client.get_database("fido-new")
transaction_collection = db.get_collection("transactions", codec_options=codec_options)
