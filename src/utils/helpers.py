from typing import Any, Union
import json
from json import JSONDecodeError
from src.utils.logger import logger

async def validate_search_q(value: str) -> Union[int, str]:
    return int(value) if value.isdigit() else value

async def json_to_dict(data: Any):
    try:
        result = json.loads(json.loads(data))
        return result
    except JSONDecodeError as e:
        logger.error(f'Helper - Provided data is not serrializible: {e}')
    except Exception as e:
        logger.error(f'Helper - unexpected error when checking is data serrializible: {e}')


