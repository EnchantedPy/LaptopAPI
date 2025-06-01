from abc import ABC, abstractmethod
from typing import Any

class DatabaseInterface(ABC):
	
	@abstractmethod
	async def get_all(self) -> list[Any]:
		raise NotImplementedError
	
	@abstractmethod
	async def add(self, data: Any) -> None:
		raise NotImplementedError
	
	@abstractmethod
	async def update(self, data: Any) -> None:
		raise NotImplementedError
	
	@abstractmethod
	async def delete(self, data: Any) -> None:
		raise NotImplementedError