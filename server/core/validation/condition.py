from typing import Any

from .reference import Ref


class Condition:

    def check(self, context: Any = None) -> bool:  #type: ignore
        pass



class Equal(Condition):
    def __init__(self, left_value: Ref | Any, right_value: Ref | Any):
        self.left_value = left_value
        self.right_value = right_value

    def check(self, context: Any = None):
        left_value = self.left_value.get(context) if isinstance(self.left_value, Ref) else self.left_value

        right_value = self.right_value.get(context) if isinstance(self.right_value, Ref) else self.right_value

        return left_value == right_value

    def __str__(self):
        return f"{self.left_value} == {self.right_value}"
