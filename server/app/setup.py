import os
import datetime
from flask import Flask
from flask.json.provider import DefaultJSONProvider
from .hooks.before_request import before_request
from .hooks.after_request import after_request
from .hooks.errors import *
import extensions

class JSONProvider(DefaultJSONProvider):
    ensure_ascii = False

    def default(self, obj): # type: ignore
        if isinstance(obj, datetime.datetime):
            print(obj)
            return obj.isoformat()
        else:
            return super().default(obj)



def setupApp():
    app = Flask(__name__, static_folder=os.path.join(extensions.rootDir, "static"), template_folder="res", static_url_path="/")

    app.json_provider_class = JSONProvider
    app.json = JSONProvider(app)

    from app import blueprints
    for bp in blueprints:
        bp.register_for_app(app, extensions.routeManager)

    
    app.before_request(before_request) # type: ignore

    app.after_request(after_request)

    setup_error_handlers(app)
    
    return app