from typing import Any, Callable

from .reference import Ref


class Condition:

    def check(self, context: Any = None) -> bool:  #type: ignore
        pass



class Equal(Condition):
    def __init__(self, leftValue:  Any, rightValue:  Any):
        self.leftValue = leftValue
        self.rightValue = rightValue

    def check(self, context: Any = None):
        if hasattr(self.leftValue, "get") and isinstance(self.leftValue.get, Callable):
            leftValue = self.leftValue.get(context)

        if hasattr(self.rightValue, "get") and isinstance(self.rightValue.get, Callable):
            rightValue = self.rightValue.get(context)


        return leftValue == rightValue

    def __str__(self):
        return f"{self.leftValue} == {self.rightValue}"

class RefIs(Condition):
    def __init__(self, name: str, value: Any):
        self.ref = Ref(name)
        self.value = value

    def check(self, context: Any = None):
        return self.ref.get(context) == self.value

    def __str__(self):
        return f"{self.ref} == {self.value}"
