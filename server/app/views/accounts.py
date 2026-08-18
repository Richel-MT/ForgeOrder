from typing import cast

from flask import  request

from app.routes.responseGenerator import ResponseInfo
from app.service.users import UserService
from app.routes.blueprint import AppBlueprint
from .exceptions import *
from app.routes.field import BodyField, NotEmpty
from core.utils import getClientIp
from app.utils import g

accountsBlueprint = AppBlueprint("accounts", __name__)

@accountsBlueprint.post("/api/auth/login",              
    arguments = [   
        BodyField("username", str, True, None, NotEmpty()),
        BodyField("password", str, True, None, NotEmpty()),
        BodyField("cover", bool, False, False)
    ],
    requiresAuth=False,
    isAdmin=False,
    responses=[
        ResponseInfo(0, "OK", dict),
        ResponseInfo(3001, "UsernameOrPasswordError", None),
        ResponseInfo(3002, "UserIsDisabled", None),
        ResponseInfo(3003, "RepeatLogin", dict),
        ResponseInfo(3004, "NewDeviceLogin", dict),
    ]
)
def login():
    logger = g.logger.getLogContext("ACCOUNTS")

    g.logger.setCategory("Login")

    username = g.args["username"]
    password = g.args["password"]
    cover = g.args["cover"]

    ip : str = cast(str, getClientIp())

    service = UserService(g.repos)

    result = service.login(username, password, ip, cover)

    if result.code == service.LOGIN.SUCCESS:
        return g.res.OK(result.data)

    elif result.code == service.LOGIN.USERNAME_OR_PASSWORD_ERROR:
        return g.res.UsernameOrPasswordError()

    elif result.code == service.LOGIN.USER_DISABLED:
        return g.res.UserIsDisabled()

    elif result.code == service.LOGIN.REPEAT_LOGIN:
        return g.res.RepeatLogin(result.data)
    
    elif result.code == service.LOGIN.NEW_DEVICE:
        return g.res.NewDeviceLogin(result.data)


        
@accountsBlueprint.post("/api/auth/logout", requiresAuth=True,
                  responses=[
                      ResponseInfo(0, "OK", None),
                      ResponseInfo(3001, "TokenInvalid", None),
                  ])
def logout():
    logger = g.logger.getLogContext("ACCOUNTS")

    token = request.headers.get("Authorization")

    try:
        token = token.split(" ")[1] #type: ignore
    except IndexError:
        # 无空格
        return g.res.TokenInvalid()
    
    service = UserService(g.repos)

    result = service.logout(token)

    if result.code == service.LOGOUT.TOKEN_INVALID:
        return g.res.TokenInvalid()

    logger.info(
        {
            "ip": getClientIp(),
            "userId": result.data["userId"],
        }, "UserLogout", g.requestId)
    

    return g.res.OK()
    


