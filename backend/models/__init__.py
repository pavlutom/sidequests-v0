from database import Base
from .user import User
from .sidequest import Sidequest

# Provide all models from the base module to satisfy `import models; models.User` syntax
__all__ = ["Base", "User", "Sidequest"]
