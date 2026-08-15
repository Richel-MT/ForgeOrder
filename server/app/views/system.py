import os

from flask import Blueprint

from core.utils import makeResponse
from app.routes.blueprint import AppBlueprint
from app.const import VERSION


systemBlueprint = AppBlueprint("system", __name__)

@systemBlueprint.route("/api/system/getSystemInfo", requiresAuth=True)
def getSystemInfo():
    return makeResponse(
        0,
        {
            "version": VERSION,
            "env": os.environ["ENV"]
        }
    )
