from fastapi import HTTPException, status

class DatabaseError(HTTPException):
	def __init__(self, detail: str = 'Database error occured'):
		super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class ConflictEntity(HTTPException):
	def __init__(self, detail: str = 'Values are already in use'):
		 super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)