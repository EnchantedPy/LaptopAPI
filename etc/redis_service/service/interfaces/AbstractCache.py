from abc import ABC, abstractmethod
from typing import Any

class AbstractCache(ABC):

	@abstractmethod
	async def _set(self, key: str, value: str) -> bool:
		...

	@abstractmethod
	async def _get(self, key: str) -> Any:
		...

	@abstractmethod
	async def _delete(self, key: str) -> bool:
		...

	@abstractmethod
	async def _expire(self, key: str, ttl: int) -> bool:
		...