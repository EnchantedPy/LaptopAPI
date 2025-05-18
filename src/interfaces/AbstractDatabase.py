from abc import ABC, abstractmethod
from typing import Any

class DatabaseInterface(ABC):
	'''Doesn't have get_one -> Any method, because research can be done by different
	model fields, it's implemented in classes which inherit from DatabaseInterface'''
	
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