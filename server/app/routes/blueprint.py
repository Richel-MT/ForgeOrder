from flask import Blueprint, Flask

from .manager import RouteManager
from .schema import RequestField, ResponseInfo

class AppBlueprint(Blueprint):
    def __init__(self, name: str, import_name: str):
        super().__init__(name, import_name)

        self.routes_ = []

    def registerForApp(self, app: Flask, routeManager: RouteManager):
        app.register_blueprint(self)

        for route in self.routes_:
            # print(route)
            routeManager.register(route["path"],
                                    route["requiresAuth"],
                                    route["isAdmin"],
                                    route["arguments"],
                                    route["responses"])
        

    def route(self, rule: str,
            arguments: list[RequestField] | None = None,
            requiresAuth: bool = False,
            isAdmin: bool = False,
            responses: list[ResponseInfo] | None = None,
            noRegister: bool = False,
            **options
            ):
        
        flask_route = super().route(rule, **options)
        
        def wrapper(f):
            if not noRegister:
                self.routes_.append({
                    "path": rule,
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
            arguments: list[RequestField] | None = None,
            responses: list[ResponseInfo] | None = None,
            **options
            ):
        
        options.setdefault("methods", ["POST"])
        return self.route(rule, arguments, requiresAuth, isAdmin, responses, **options)
    
    
        
    

        

        

