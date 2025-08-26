
class CustomException(Exception):
    def __init__(self, message: str, status_code: int = 500, details: str = None):
        self.message = message 
        self.status_code = status_code
        self.details = details 
        super().__init__(self.message)
