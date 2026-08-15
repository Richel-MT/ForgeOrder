from typing import cast

from flask import current_app
from werkzeug.local import LocalProxy

from .manager import RouteManager

def _getRouteManager() -> RouteManager:
    return cast(RouteManager, current_app.routeManager) #type: ignore

routeManager = cast(RouteManager, LocalProxy(_getRouteManager))
