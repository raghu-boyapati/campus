from fastapi import HTTPException, status


class StudentNotFoundException(HTTPException):
    def __init__(self, detail: str = "Student not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class CommentNotFound(HTTPException):
    def __init__(self, status_code, detail="Comment not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class InvalidCredentialsException(HTTPException):
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        )
