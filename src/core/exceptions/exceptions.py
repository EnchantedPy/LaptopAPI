from fastapi import HTTPException, status


# ------- Database Errors ------

class DatabaseException(HTTPException):
	def __init__(self, detail: str = 'Database error occured'):
		super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


class DatabaseIntegrityException(HTTPException):
	def __init__(self, detail: str = 'Database integrity error occured'):
		super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class DatabaseDataException(HTTPException):
	def __init__(self, detail: str = 'Database data error occured'):
		super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class DatabaseOperationalException(HTTPException):
	def __init__(self, detail: str = 'Database operational error occured'):
		super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)
            
class DatabaseConfigurationException(HTTPException):
      def __init__(self, detail: str = 'Database configuration error occured'):
            super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


# ------- S3 Errors ------

class S3Exception(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected S3 error occurred"
        )
        

class S3NoCredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 credentials error occurred"
        )


class S3ConnectionException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 connection error occurred"
        )


class S3ClientException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 client error occurred"
        )


class S3ParameterValidationException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="S3 parameter validation error occurred"
        )

