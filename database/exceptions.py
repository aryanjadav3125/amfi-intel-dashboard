class DBError(Exception):
    """Base exception for all database operations."""
    pass

class DBConnectionError(DBError):
    """Raised when connecting to the database fails."""
    pass

class DBInsertError(DBError):
    """Raised when record insertions fail."""
    pass
