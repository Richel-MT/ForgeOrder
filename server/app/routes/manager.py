from .schema import RoutesInfo
from .responseGenerator import ResponseGenerator, ResponseInfo
from .exceptions import *
from .field import BodyField


class RouteManager:
    def __init__(self):

        self.routes: dict[str, RoutesInfo] = {}

    def register(self, path: str,
                 requiresAuth: bool= False,
                 isAdmin: bool = False,
                 args: list[BodyField] | None = None,
                 responses: list[ResponseInfo] | None = None):

        if args is None:
            args = []

        if path in self.routes:
            raise RouteAlreadyRegisteredError(path)
        
        args_ = {}

        for arg in args:
            args_[arg.key] = arg

        self.routes[path] = { # type: ignore
            "isAdmin": isAdmin,
            "requiresAuth": requiresAuth,
            "args": args_,
            "responses": responses,
        }

        

    def hasArguments(self, path: str):
        if path in self.routes and len(self.routes[path]["args"]) > 0:  
            return True
        else:
            return False

    def validateArguments(self, path: str, args: dict):
        if path not in self.routes:
            return {}
        
        routesInfo = self.routes[path] # 所有args的字段定义

        finalArguments = {}

        errors = {}

        for key, field in routesInfo["args"].items():
            if key in args.keys():
                # key本身存在，验证类型
                if not isinstance(args[key], field.valueType):
                    errors[key] = InvalidArgumentTypeError(key, field.valueType, type(args[key]))


                # 执行Validator
                if not field.validator:
                    finalArguments[key] = args[key]
                    continue

                result = field.validator.validate(args[key])

                if result.success:
                    finalArguments[key] = args[key]
                    continue
                else:
                    errors[key] = ArgumentValidationError(key, result.error) #type: ignore
                

                
            elif field.required:
                # key不存在，必填项。
                errors[key] = MissingRequiredArgumentError(field.key)
            else:
                # key不存在，非必填项。
                finalArguments[key] = field.default

        if errors:
            return False, errors
        else:
            return True, finalArguments


    

    def getAuthConfig(self, path: str):
        if path not in self.routes:
            return False, None
        
        else:
            return True, {
                "requiresAuth": self.routes[path]["requiresAuth"],
                "isAdmin": self.routes[path]["isAdmin"]
            }
        
        
        