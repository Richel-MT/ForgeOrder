from typing import Any

class ContextAccessError(Exception):

    def __init__(self, context: Any):
        self.context = context

        super().__init__("Cannot get value from context, context must provide a get() method")
from typing import Any

class ContextAccessError(Exception):

    def __init__(self, context: Any):
        self.context = context

        super().__init__("Cannot get value from context, context must provide a get() method")