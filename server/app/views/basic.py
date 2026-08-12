
import os

from flask import (Blueprint, current_app, send_from_directory, request)
from app.routes.app_bp import AppBlueprint
import extensions

basic_bp = AppBlueprint("basic", __name__)

@basic_bp.route("/routeInfo", no_register=True)
def route_info():
    route_name: str = request.args.get("path") #type: ignore

    route = extensions.routeManager.routes.get(route_name)

    if route is None:
            return {
                "error": "Route not found."
            }

    
    arguments = []

    for _, argument in route["args"].items():
         arguments.append({
            "key": argument.key,
            "type": str(argument.value_type),
            "required": argument.required,
            "default": argument.default,
        })

    responses = []

    for response in route["responses"]:
        responses.append({
             "status": response.status_code,
             "name": response.name,
             "data_type": str(response.data_type),
        })


    return {
            "path": route_name,
            "auth": route["auth"],
            "is_admin": route["is_admin"],
            "arguments": arguments,
            "responses": responses,
        }

@basic_bp.route("/", defaults={"path": ""}, no_register=True)
@basic_bp.route("/<path:path>", no_register=True)
def index(path: str = ""):
    if "." in path:
        file_path = os.path.join(current_app.static_folder, path) #type: ignore
        if os.path.exists(file_path):
            return send_from_directory(current_app.static_folder, path) #type: ignore
    
    return send_from_directory(current_app.static_folder, "index.html") #type: ignore


    
