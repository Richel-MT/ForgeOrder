from typing import Any

class UnsupportedValidatorError(Exception):

    '''
    使用FunctionHandler，函数的返回值结构不正确
    '''
    def __init__(self, validatorClass: type):
        self.validatorClass = validatorClass
        
        super().__init__(f"Implemented {validatorClass.__name__} in an unsupported way.")



class ContextMissingError(Exception):

    def __init__(self, context: Any):
        self.context = context

        super().__init__("Context must provide a get() method, or be empty.")

class UnsupportedTypeError(Exception):
    '''
    无法处理这个值的类型。
    '''
    def __init__(self, validatorClass: type, expectedType: type, valueType: type):
        self.validatorClass = validatorClass
        self.expectedType = expectedType
        self.expectedType = expectedType
        self.valueType = valueType

        super().__init__(
            f"Validator ' {self.validatorClass.__name__}' does not support type {self.valueType}, expected type is {expectedType}."
        )

class NotIterableError(Exception):
    '''
    传入的值不是可迭代对象
    '''
    def __init__(self, validatorClass: type, valueType: type):
        self.validatorClass = validatorClass
        self.valueType = valueType

        super().__init__(
            f"Validator ' {self.validatorClass.__name__}' requires an iterable value, but got {self.valueType}."
        )