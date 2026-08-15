from app.exceptions import UserError

class SettingsInitError(UserError):
    def __init__(self, msg: str):
        self.msg = msg
        self.hint = "更改数据库表的记录或使用'--fix'参数尝试修复此问题。"
        super().__init__(msg)


class SettingsException(Exception):
    pass


class SettingNotFoundError(SettingsException):
    def __init__(self, key: str):
        self.key = key

        super().__init__(f"Setting '{key}' not found.")

class SettingTypeError(SettingsException):
    def __init__(self, key: str, expectedType: type, valueType: type):
        self.key = key
        self.expectedType = expectedType
        self.valueType = valueType
        
        super().__init__(f"Setting '{key}' expect type {expectedType}, but it is {valueType}.")
        
class SettingValidateError(SettingsException):
    def __init__(self, key: str, msg: str):
        self.key = key  
        self.msg = msg
        
        super().__init__(f"Setting '{key}' validate failed: {msg}")