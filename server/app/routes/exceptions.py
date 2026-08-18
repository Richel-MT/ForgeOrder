

from core.validation.errors import ValidationError


class RouterManagerException(Exception):
    pass

class RouteAlreadyRegisteredError(RouterManagerException):
    def __init__(self, path: str):
        self.path = path

        super().__init__(f"Route '{self.path}' is Already Registered.")


## 请求头中的参数验证错误
class BodyParametersException(RouterManagerException):
    key: str
    msg: str

class MissingRequiredParameterError(BodyParametersException):
    def __init__(self, key: str):
        self.key = key
        self.msg = f"Argument '{key}' is required."
        super().__init__(self.msg)

class ParameterTypeError(BodyParametersException):
    def __init__(self, key: str, expectedType: type, valueType: type):
        self.key = key
        self.expectedType = expectedType
        self.valueType = valueType
        self.msg = f"Argument '{key}' expected {expectedType.__name__} type, got {valueType.__name__} type."
        super().__init__(self.msg)

class ParameterValidationError(BodyParametersException):
    def __init__(self, key: str, error: ValidationError):
        self.key = key
        self.error = error

        self.msg = f"Argument '{key}' validation error: {error}"
        super().__init__(self.msg)

# 路径参数中的错误
class PathParameterException(RouterManagerException):
    path: str # URL 路径
    key: str # 参数的键
    value: str # 参数具体的值
    msg : str # 消息

    def __init__(self, path: str, key: str, value: str, msg: str):
        self.path = path
        self.key = key
        self.value = value
        self.msg = msg

        super().__init__(msg)

    def _pathHints(self):
        if self.value not in self.path:
            raise ValueError(f"Value '{self.value}' not found in path '{self.path}'")

        index = self.path.find(self.value)

        return f"{self.path}\n{index * " "}{"^" * len(self.value)}"

class PathParameterNotFoundError(PathParameterException):

    def __init__(self, path: str, key: str):
        super().__init__(path, key, "", f"Path parameter '{key}' not found in path '{path}'.")

class PathParameterTypeError(PathParameterException):
    def __init__(self, path: str, key: str, value: str, expectedType: type,):
        self.expectedType = expectedType
        self.valueType = type(value)

        super().__init__(path, key, value, f"Path parameter '{key}' expected {expectedType.__name__} type, got {self.valueType.__name__} type. At: \n{self._pathHints()}")

class PathParameterValidationError(PathParameterException):
    def __init__(self, path: str, key: str, value: str, error: ValidationError):
        self.error = error
        self.msg = f"Path parameter '{key}' validation error: {error} At: \n{self._pathHints()}"

        super().__init__(path, key, value, self.msg)










        

