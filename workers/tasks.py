from workers.app import app
from src.utils.logger import logger

@app.task(name='loginfo')
def loginfo():
    for i in range(1, 11):
        logger.info(f'{i}. info logged')
