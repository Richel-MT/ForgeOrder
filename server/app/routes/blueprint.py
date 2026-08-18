from flask import Blueprint, Flask

from .manager import RouteManager
from .schema import RequestParameterField, ResponseInfo

class AppBlueprint(Blueprint):
    def __init__(self, name: str, import_name: str):
        super().__init__(name, import_name)

        self.routes_ = []

    def registerForApp(self, app: Flask, routeManager: RouteManager):
        app.register_blueprint(self)

        for route in self.routes_:
            # print(route)
            routeManager.register(route["endpoint"],
                                    route["requiresAuth"],
                                    route["isAdmin"],
                                    route["arguments"],
                                    route["responses"])
        

    def route(self, rule: str,
            arguments: list[RequestParameterField] | None = None,
            requiresAuth: bool = False,
            isAdmin: bool = False,
            responses: list[ResponseInfo] | None = None,
            noRouteInfo: bool = False,
            **options
            ):
        
        flask_route = super().route(rule, **options)
        
        def wrapper(f):
            if not noRouteInfo:
                self.routes_.append({
                    "endpoint": f"{self.name}.{f.__name__}",
                    "requiresAuth": requiresAuth,
                    "isAdmin": isAdmin,
                    "arguments": arguments,
                    "responses": responses,
                })

            return flask_route(f)
        
        return wrapper
    
    def get(self, rule: str,
            requiresAuth: bool = False,
            isAdmin: bool = False,
            responses: list[ResponseInfo] | None = None,
            **options
            ):
        
        options.setdefault("methods", ["GET"])
        return self.route(rule, None, requiresAuth, isAdmin, responses, **options)
    
    def post(self, rule: str,
            requiresAuth: bool = False,
            isAdmin: bool = False,
            arguments: list[RequestParameterField] | None = None,
            responses: list[ResponseInfo] | None = None,
            **options
            ):
        
        options.setdefault("methods", ["POST"])
        return self.route(rule, arguments, requiresAuth, isAdmin, responses, **options)
    
    
        
    

        

        

