from abc import ABC, abstractmethod
from typing import Any

class StorageInterface(ABC):
	
	@abstractmethod
	async def put(self, key: Any, value: Any) -> None:
		raise NotImplementedError
	
	@abstractmethod
	async def get(self, key: Any) -> Any:
		raise NotImplementedError
	
	@abstractmethod
	async def delete(self, key: Any) -> None:
		raise NotImplementedError