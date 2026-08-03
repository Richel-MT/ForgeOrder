from app.exceptions import UserError




class TypingConvertError(SettingsException):
    def __init__(self, value, convert_type: type , msg: str = ""):
        self.value = value
        self.convert_type = convert_type
        
        super().__init__(msg)

     