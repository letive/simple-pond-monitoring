class Error(Exception):
    """Base class for other exceptions"""
    pass


class ErrorIndex(Error):
    """Raised when the index dataframe selection not found or error"""
    pass