import os

from flask import Blueprint

import extensions
from core.utils import makeResponse
from app.routes.blueprint import AppBlueprint



system_bp = AppBlueprint("system", __name__)

@system_bp.route("/api/system/getSystemInfo", requiresAuth=True)
def get_system_info():
    return makeResponse(
        0,
        {
            "version": extensions.version,
            "env": os.environ["ENV"]
        }
    )
