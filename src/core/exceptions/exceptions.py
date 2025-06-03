from fastapi import HTTPException, status

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

