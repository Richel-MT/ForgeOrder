from typing import Any, Callable

from .reference import Ref


class Condition:

    def check(self, context: Any = None) -> bool:  #type: ignore
        pass



class Equal(Condition):
    def __init__(self, left_value:  Any, right_value:  Any):
        self.left_value = left_value
        self.right_value = right_value

    def check(self, context: Any = None):
        if hasattr(self.left_value, "get") and isinstance(self.left_value.get, Callable):
            left_value = self.left_value.get(context)

        if hasattr(self.right_value, "get") and isinstance(self.right_value.get, Callable):
            right_value = self.right_value.get(context)


        return left_value == right_value

    def __str__(self):
        return f"{self.left_value} == {self.right_value}"

class RefIs(Condition):
    def __init__(self, name: str, value: Any):
        self.ref = Ref(name)
        self.value = value

    def check(self, context: Any = None):
        return self.ref.get(context) == self.value

    def __str__(self):
        return f"{self.ref} == {self.value}"
