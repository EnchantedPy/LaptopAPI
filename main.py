#from typing import Annotated
from fastapi import FastAPI
import uvicorn
from workers.tasks import loginfo
# from config.settings import SAppSettings
# from src.schemas.schemas import UserAddSchema, UserDeleteSchema, UserUpdateSchema, LaptopAddSchema, LaptopDeleteSchema, LaptopUpdateSchema
# from src.utils.UnitOfWork import SQLAlchemyUoW, SQLAlchemyUoWInterface
# from src.services.UserService import UserService
# from src.utils.logger import logger
# from src.services.LaptopService import LaptopService
# from src.services.JsonDataService import JsonDataService
# from src.utils.UnitOfWork import S3UoWInterface, S3UoW
# from src.services.UserActivityService import UserActivityService
# from src.schemas.schemas import UserActivityAddSchema, UserActivityDeleteSchema

# SqlaUoWDep = Annotated[SQLAlchemyUoWInterface, Depends(SQLAlchemyUoW)]

# S3UoWDep = Annotated[S3UoWInterface, Depends(S3UoW)]
app = FastAPI(title='Test stack api')


@app.get('/root')
async def root():
	return {'status': 'success'}

@app.get('/celery_task')
def run_celery_task():
	loginfo.delay()


if __name__ == '__main__':
	uvicorn.run('main:app', host='0.0.0.0', port=8000, reload=True)