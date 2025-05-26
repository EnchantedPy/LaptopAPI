from fastapi import HTTPException, status


# ------- Database Errors ------

class DatabaseException(HTTPException):
	def __init__(self, detail: str = 'Database error occured'):
		super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class DatabaseIntegrityException(HTTPException):
	def __init__(self, detail: str = 'Database integrity error occured: username already taken | required field is empty'):
		super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class DatabaseDataException(HTTPException):
	def __init__(self, detail: str = 'Database data error occured: incorrect data type or format'):
		super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class DatabaseOperationalException(HTTPException):
	def __init__(self, detail: str = 'Database operational error occured: something went wrong when processing entity'):
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
        

# --------- Service Errors -------

class ActivityNotFoundException(HTTPException):
      def __init__(self, detail):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
        
class UserNotFoundException(HTTPException):
      def __init__(self, detail):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )
        
class NoChangesProvidedException(HTTPException):
      def __init__(self, detail):
        super().__init__(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=detail
        )
        
class LaptopNotFoundException(HTTPException):
      def __init__(self, detail):
        super().__init__(
            status_code=status.HTTP_204_NO_CONTENT,
            detail=detail
        )

class LaptopTemplatesLimitException(HTTPException):
      def __init__(self, detail):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )
        
class IncorrectSubmitPassword(HTTPException):
     def __init__(self, detail):
          super().__init__(
               status_code=status.HTTP_409_CONFLICT,
               detail=detail
			 )
        





# class AlreadyLoggedInException(HTTPException):
#     def __init__(self, detail: str):
#         super().__init__(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=detail
#         )

# class AuthRequiredException(HTTPException):
#     def __init__(self, detail: str):
#         super().__init__(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=detail
#         )

# class AdminPrivilegesRequiredException(HTTPException):
#     def __init__(self, detail: str):
#         super().__init__(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail=detail
#         )

# class InvalidTokenException(HTTPException):
#     def __init__(self, detail: str):
#         super().__init__(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=detail
#         )

# class FailedTokenRefreshException(HTTPException):
#     def __init__(self, detail: str):
#         super().__init__(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=detail
#         )

# class NoValidTokensFoundException(HTTPException):
#     def __init__(self, detail: str):
#         super().__init__(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail=detail
#         )

