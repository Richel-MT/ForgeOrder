from typing import Any

class UnsupportedVerifyHandlerError(Exception):

    '''
    使用FunctionHandler，函数的返回值结构不正确
    '''
    def __init__(self, verify_handler_class: type):
        self.verify_handler_class = verify_handler_class
        
        super().__init__(f"Implemented {verify_handler_class.__name__} in an unsupported way.")



class ContextMissingError(Exception):

    def __init__(self, context: Any):
        self.context = context

        super().__init__("Context must provide a get() method, or be empty.")