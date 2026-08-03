import os

from flask import Flask

from .hooks.before_request import before_request
from .hooks.after_request import after_request
from .hooks.errors import *
import extensions

def setup_app():
    app = Flask(__name__, static_folder=os.path.join(extensions.root_dir, "static"), template_folder="res", static_url_path="/")

    app.json.ensure_ascii = False

    from app import blueprints
    for bp in blueprints:
        bp.register_for_app(app, extensions.route_manager)

    
    app.before_request(before_request) # type: ignore

    app.after_request(after_request)

    setup_error_handlers(app)
    
    return app