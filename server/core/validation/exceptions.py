from typing import Any


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

class NonMergeableValidatorError(Exception):
    '''
    不可合并的验证器
    '''

    def __init__(self, validatorClass: type):
        self.validatorClass = validatorClass

        super().__init__(f"Validator ' {self.validatorClass.__name__}' is not mergeable.")

