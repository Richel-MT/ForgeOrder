from typing import Any, Callable

from .exceptions import ContextMissingError


class ValueProvider:
    def get(self, context: Any):
        pass

class Ref(ValueProvider):

    def __init__(self, name:str):
        self.name = name

    def get(self, context: Any):
        if hasattr(context, "get"):
            return context.get(self.name)
        else:
            raise ContextMissingError(context)

    def __str__(self):
        return self.name


class Computed(ValueProvider):
    def __init__(self, func: Callable, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def get(self, context: Any=None):
        return self.func(*self.args, **self.kwargs)