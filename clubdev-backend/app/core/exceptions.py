# exceptions.py
class DatabaseError(Exception):
    """Exception raised for errors in the database."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class ItemNotFoundError(Exception):
    """Exception raised when an item is not found in the database."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)