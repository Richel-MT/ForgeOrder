from typing import cast

from flask import  request, g
from werkzeug.security import check_password_hash

from app.routes.res_generator import ResponseInfo
from app.service.users import UserService
import extensions
from app.routes.app_bp import AppBlueprint
from core.utils import get_client_ip, make_response
from ..db.connections import get_database
from .exceptions import *
from app.routes.field import RequestField, NotEmpty

accounts_bp = AppBlueprint("accounts", __name__)

@accounts_bp.post("/api/auth/login",              
    arguments = [   
        RequestField("username", str, True, None, NotEmpty()),
        RequestField("password", str, True, None, NotEmpty()),
        RequestField("cover", bool, False, False)
    ],
    auth=False,
    is_admin=False,
    responses=[
        ResponseInfo(0, "OK", dict),
        ResponseInfo(3001, "UsernameOrPasswordError", None),
        ResponseInfo(3002, "UserIsDisabled", None),
        ResponseInfo(3003, "RepeatLogin", dict),
        ResponseInfo(3004, "NewDeviceLogin", dict),
    ]
)
def login():
    logger = g.logger.get_log_context("ACCOUNTS")

    g.logger.set_category("LOGIN_REQUEST")

    username = g.args["username"]
    password = g.args["password"]
    cover = g.args["cover"]

    ip : str = cast(str, get_client_ip())

    service = UserService(g.repos, extensions.config)

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


        
@accounts_bp.post("/api/auth/logout", auth=True,
                  responses=[
                      ResponseInfo(0, "OK", None),
                      ResponseInfo(3001, "TokenInvalid", None),
                  ])
def logout():
    logger = g.logger.get_log_context("ACCOUNTS")

    token = request.headers.get("Authorization")

    
    token = token.split(" ")[1] #type: ignore
    
    service = UserService(g.repos, extensions.config)
    result = service.logout(token)

    if result.code == service.LOGOUT.TOKEN_INVALID:
        return g.res.TokenInvalid()

    logger.info(
        {
            "ip": get_client_ip(),
            "user_id": result.data["user_id"],
        }, "UserLogout", g.request_id)
    

    return g.res.OK()
    



@accounts_bp.route("/test_print")
def test_print():
    from app.printer.receipt import Receipt

    receipt = Receipt()
    
    receipt.build.text("123")
    receipt.build.qr_code("https://baidu.com")

    
    extensions.print_manager.new(receipt)

    return "ok"