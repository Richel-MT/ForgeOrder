import os

from flask import Blueprint

import extensions
from core.utils import makeResponse
from app.routes.blueprint import AppBlueprint



systemBlueprint = AppBlueprint("system", __name__)

@systemBlueprint.route("/api/system/getSystemInfo", requiresAuth=True)
def getSystemInfo():
    return makeResponse(
        0,
        {
            "version": extensions.version,
            "env": os.environ["ENV"]
        }
    )
