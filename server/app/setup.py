import os
import datetime
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from .hooks.beforeRequest import beforeRequest
from .hooks.afterRequest import afterRequest
from .hooks.errors import *
import extensions

class JSONProvider(DefaultJSONProvider):
    ensure_ascii = False

    def default(self, obj): # type: ignore
        if isinstance(obj, datetime.datetime):
            return obj.isoformat()
        else:
            return super().default(obj)



def setupApp():
    app = Flask(__name__, static_folder=os.path.join(extensions.rootDir, "static"), template_folder="res", static_url_path="/")

    app.json_provider_class = JSONProvider
    app.json = JSONProvider(app)

    from app import blueprints
    for bp in blueprints:
        bp.registerForApp(app, extensions.routeManager)

    
    app.before_request(beforeRequest) # type: ignore

    app.after_request(afterRequest)

    setupErrorHandlers(app)
    
    return app