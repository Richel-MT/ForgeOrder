from typing import Any, Callable, TYPE_CHECKING



class Condition:
    def check(self, context: Any = None) -> bool:  #type: ignore
        pass


class Equal(Condition):
    def __init__(self, leftValue:  Any, rightValue:  Any):
        self.leftValue = leftValue
        self.rightValue = rightValue

    def check(self, context: Any = None):
        if hasattr(self.leftValue, "get") and isinstance(self.leftValue.get, Callable):
            leftValue : Any= self.leftValue.get(context)
        else:
            raise AttributeError(f"{self.leftValue} does not have a 'get' method.")

        if hasattr(self.rightValue, "get") and isinstance(self.rightValue.get, Callable):
            rightValue : Any = self.rightValue.get(context)
        else:
            raise AttributeError(f"{self.rightValue} does not have a 'get' method.")


        return leftValue == rightValue

    def __str__(self):
        return f"{self.leftValue} == {self.rightValue}"

