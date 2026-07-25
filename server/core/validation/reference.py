from typing import Any

from .exceptions import ContextMissingError

class Ref:

    def __init__(self, name:str):
        self.name = name

    def get(self, context: Any):
        if hasattr(context, "get"):
            return context.get(self.name)
        else:
            raise ContextMissingError(context)

    def __str__(self):
        return self.name
