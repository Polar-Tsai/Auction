class BusinessException(Exception):
    """
    Business logic error (e.g. invalid status, insufficient funds).
    User action required.
    """
    def __init__(self, message, code='BUSINESS_ERROR'):
        self.message = message
        self.code = code
        super().__init__(message)

class SystemException(Exception):
    """
    System internal error (e.g. DB connection failed, IO error).
    Admin attention required.
    """
    def __init__(self, message, original_exception=None):
        self.message = message
        self.original_exception = original_exception
        super().__init__(message)
