from abc import ABC, abstractmethod
from typing import Any

class CacheInterface(ABC):
	@abstractmethod
	async def get(self, key: str) -> Any:
		raise NotImplementedError
	
	@abstractmethod
	async def put(self, key: str, data: Any) -> Any:
		raise NotImplementedError
	
	@abstractmethod
	async def delete(self, key: str) -> None:
		raise NotImplementedError
	
	@abstractmethod
	async def set_ttl(self, key: str, ttl: int) -> None:
		raise NotImplementedError
	
	@abstractmethod
	async def clear(self) -> None:
		raise NotImplementedError