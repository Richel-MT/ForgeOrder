
import os

from flask import (Blueprint, current_app, send_from_directory, request)
from app.routes.blueprint import AppBlueprint
from app.routes import routeManager


basicBlueprint = AppBlueprint("basic", __name__)

@basicBlueprint.route("/routeInfo", noRegister=True)
def routeInfo():
    routeName: str = request.args.get("path") #type: ignore

    route = routeManager.routes.get(routeName)

    if route is None:
            return {
                "error": "Route not found."
            }

    
    arguments = []

    for _, argument in route["params"].items():
         arguments.append({
            "key": argument.key,
            "type": str(argument.valueType),
            "required": argument.required,
            "default": argument.default,
        })

    responses = []

    for response in route["responses"]:
        responses.append({
             "status": response.status_code,
             "name": response.name,
             "dataType": str(response.dataType),
        })


    return {
            "path": routeName,
            "auth": route["requiresAuth"],
            "isAdmin": route["isAdmin"],
            "arguments": arguments,
            "responses": responses,
        }

@basicBlueprint.route("/", defaults={"path": ""}, noRegister=True)
@basicBlueprint.route("/<path:path>", noRegister=True)
def index(path: str = ""):
    if "." in path:
        filePath = os.path.join(current_app.static_folder, path) #type: ignore
        if os.path.exists(filePath):
            return send_from_directory(current_app.static_folder, path) #type: ignore
    
    return send_from_directory(current_app.static_folder, "index.html") #type: ignore


    
