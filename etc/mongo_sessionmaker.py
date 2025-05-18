from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient
from src.models.mongo_models import UserActivityState
from beanie import init_beanie
from config.settings import SAppSettings

# https://claude.ai/chat/2aae8927-89da-4596-98c4-abc6ea8d3c05

class mongo_sessionmaker:
    def __init__(self, _mongo_url, _mongo_name):
        self._mongo_url = _mongo_url
        self._mongo_name = _mongo_name
        self._document_models = [UserActivityState]
        
    async def __call__(self) -> AsyncIOMotorDatabase:
        client = AsyncIOMotorClient(self._mongo_url)
        mongo_db = client[self._mongo_name]
        
        await init_beanie(database=mongo_db, document_models=self._document_models)
        
        setattr(mongo_db, '_client', client)
        
        return mongo_db
    

mongo_session_maker = mongo_sessionmaker(SAppSettings.mongo_url, SAppSettings.mongo_name)