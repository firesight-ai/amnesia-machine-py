class HAMError(Exception):
    """Custom error class for HAM-related exceptions."""
    def __init__(self, message):
        super().__init__(message)
        self.name = "HAMError"
