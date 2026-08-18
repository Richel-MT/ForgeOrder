from .schema import RoutesInfo
from .responseGenerator import ResponseGenerator, ResponseInfo
from .exceptions import *
from .field import BodyField, PathField, RequestParameterField


class RouteManager:
    def __init__(self):

        self.routes: dict[str, RoutesInfo] = {}

    def register(self, endpoint: str,
                 requiresAuth: bool= False,
                 isAdmin: bool = False,
                 params: list[RequestParameterField] | None = None,
                 responses: list[ResponseInfo] | None = None):

        if params is None:
            params = []

        if endpoint in self.routes:
            raise RouteAlreadyRegisteredError(endpoint)
        
        params_ = {}

        for arg in params:
            params_[arg.key] = arg

        self.routes[endpoint] = { # type: ignore
            "isAdmin": isAdmin,
            "requiresAuth": requiresAuth,
            "params": params_,
            "responses": responses,
        }

        

    def hasParameters(self, endpoint: str):
        if endpoint in self.routes and len(self.routes[endpoint]["params"]) > 0:  
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


    def validateParameters(self, endpoint: str | None, path: str, bodyParams: dict, pathParams: dict):

        routeInfo = self.routes.get(endpoint, None) #type: ignore

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
        bodyErrors, bodyFinalParameters = self._validateBodyParameters(bodyFields, bodyParams)
        errors.update(bodyErrors)
        finalParameters.update(bodyFinalParameters)

        pathErrors, pathFinalParameters = self._validatePathParameters(path, pathFields, pathParams)
        errors.update(pathErrors)
        finalParameters.update(pathFinalParameters)

        # 返回最终结果
        return errors, finalParameters



    def getAuthConfig(self, endpoint: str):
        if endpoint not in self.routes:
            return False, None
        
        else:
            return True, {
                "requiresAuth": self.routes[endpoint]["requiresAuth"],
                "isAdmin": self.routes[endpoint]["isAdmin"]
            }
        
        
    def getResponseInfo(self, endpoint: str | None):
        if endpoint is None:
            return []
        
        result = self.routes.get(endpoint, None)

        if result:
            return result["responses"]
        else:
            return []