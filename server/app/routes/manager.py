from .schema import RoutesInfo
from .responseGenerator import ResponseGenerator, ResponseInfo
from .exceptions import *
from .field import BodyField, PathField, RequestParameterField


class RouteManager:
    def __init__(self):

        self.routes: dict[str, RoutesInfo] = {}

    def register(self, path: str,
                 requiresAuth: bool= False,
                 isAdmin: bool = False,
                 params: list[RequestParameterField] | None = None,
                 responses: list[ResponseInfo] | None = None):

        if params is None:
            params = []

        if path in self.routes:
            raise RouteAlreadyRegisteredError(path)
        
        params_ = {}

        for arg in params:
            params_[arg.key] = arg

        self.routes[path] = { # type: ignore
            "isAdmin": isAdmin,
            "requiresAuth": requiresAuth,
            "args": params_,
            "responses": responses,
        }

        

    def hasParameters(self, path: str):
        if path in self.routes and len(self.routes[path]["params"]) > 0:  
            return True
        else:
            return False

    def _validateBodyParameters(self, paramatersInfo: dict[str, BodyField], params: dict):
        errors = {}

        finalParameters = {}

        for key, field in paramatersInfo.items():
            if key in params.keys():
                # key本身存在，验证类型
                if not isinstance(params[key], field.valueType):
                    errors[key] = ParameterTypeError(key, field.valueType, type(params[key]))

                # 执行Validator
                if not field.validator:
                    finalParameters[key] = params[key]
                    continue

                result = field.validator.validate(params[key])

                if result.success:
                    finalParameters[key] = params[key]
                    continue
                else:
                    errors[key] = ParameterValidationError(key, result.error) #type: ignore
            elif field.required:
                # key不存在，必填项。
                errors[key] = MissingRequiredParameterError(field.key)
            else:
                # key不存在，非必填项。
                finalParameters[key] = field.default

        return errors, finalParameters

    def _validatePathParameters(self, path: str, paramatersInfo: dict[str, PathField], params: dict):
        errors = {}

        finalParameters = {}

        for key, field in paramatersInfo.items():
            # 判断参数是否存在
            if key in params.keys():
                # 参数存在

                # 验证类型
                if not isinstance(params[key], field.valueType):
                    errors[key] = ParameterTypeError(key, field.valueType, type(params[key]))

                # 执行Validator
                if not field.validator:
                    finalParameters[key] = params[key]
                    continue

                result = field.validator.validate(params[key])

                if result.success:
                    finalParameters[key] = params[key]
                    continue
                else:
                    errors[key] = PathParameterValidationError(path, key, params[key], result.error) #type: ignore
                
            else:
                # 参数不存在
                errors[key] = MissingRequiredParameterError(key)

        return errors, finalParameters


    def validateParameters(self, path: str, params: dict):

        routeInfo = self.routes.get(path, None)

        if not routeInfo:
            return {}

        errors = {}

        finalParameters = {}

        bodyFields = {}
        pathFields = {}

        # 遍历routeInfo["params"]，拆分bodyField和pathField
        for key, field in routeInfo["params"].items():
            if isinstance(field, BodyField):
                bodyFields[key] = field
            elif isinstance(field, PathField):
                pathFields[key] = field
            else:
                raise ValueError(f"Invalid parameter type: {type(field)}")

        # 分别执行验证，合并结果
        bodyErrors, bodyFinalParameters = self._validateBodyParameters(bodyFields, params)
        errors.update(bodyErrors)
        finalParameters.update(bodyFinalParameters)

        pathErrors, pathFinalParameters = self._validatePathParameters(path, pathFields, params)
        errors.update(pathErrors)
        finalParameters.update(pathFinalParameters)

        # 返回最终结果
        return errors, finalParameters



    def getAuthConfig(self, path: str):
        if path not in self.routes:
            return False, None
        
        else:
            return True, {
                "requiresAuth": self.routes[path]["requiresAuth"],
                "isAdmin": self.routes[path]["isAdmin"]
            }
        
        
        