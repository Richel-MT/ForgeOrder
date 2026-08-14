import uuid
import time

from flask import request, g

from app.db.connections import getDatabase
from app.service.users import UserService
import extensions
from core.utils.server import makeResponse, getClientIp
from app.log import RequestLogContext
from app.routes.responseGenerator import ResponseGenerator

def _handle_auth():
    # 获取日志上下文
    logger = g.logger.getLogContext("BeforeRequest")

    if  request.path.startswith("/api/"):
        check_result, route_data = extensions.routeManager.getAuthConfig(request.path)
        
        if not check_result:
            # 路由不存在
            return makeResponse(
                1003,
                None
            ), 404
        

        if not route_data["requiresAuth"]: #type: ignore
            # 无需认证的api继续请求
            return None
        else:
            # 需要认证的api请求
            pass
    else:
        # 非api请求，继续访问
        return None
    
    # 从请求头中获取Token
    token = request.headers.get("Authorization", None)

    # 检查Token是否存在
    if token is None:
        # Token不存在
        return makeResponse(
            2001,
            None
        ), 401
    
    elif token.startswith("Bearer "):
        # Token格式正确
        token = token.split(" ")[1] # 提取token部分
    else:
        # Token格式错误
        return makeResponse(
            2003,
            None
        ), 401

    # 使用UserService验证Token
    service = UserService(g.repos, extensions.config)

    result = service.check_token(token)
    
    if result.code != service.AUTH.SUCCESS:
        # 验证失败，处理错误
        match result.code:
            case service.AUTH.TOKEN_INVALID:
                # Token无效
                logger.info({
                    "ip": getClientIp(),
                    "error": "InvalidToken"
                }, "AuthError")

                return makeResponse(
                    2003,
                    None
                ) , 401
            case service.AUTH.TOKEN_EXPIRED:
                # Token过期
                logger.info({
                    "ip": getClientIp(),
                    "error": "TokenExpire"
                }, "AuthError")
                

                return makeResponse(
                    2004,
                    None
                ) , 401
            case service.AUTH.TOKEN_LOGOUT:
                # 用户已退出登录
                logger.info({
                    "ip": getClientIp(),
                    "error": "TokenLogout"
                }, "AuthError")
                # 用户退出登录
                return makeResponse(
                    2003,
                    None
                ) , 401
            case service.AUTH.TOKEN_OLD_DEVICE:
                # 旧设备登录
                logger.info({
                    "ip": getClientIp(),
                    "error": "OldDevice"
                }, "AuthError")

                return makeResponse(
                    2005,
                    None
                ) , 401
    else:
        # Token有效

        # 判断Token记录的ip与请求的ip是否一致
        token_info: dict = result.data #type: ignore
        if token_info["ip"] != getClientIp(): # type: ignore
            # ip不一致
            logger.info({
                "ip": getClientIp(),
                "token_ip": token_info["ip"],
                "error": "IPNotMatch"
            }, "AuthError") # type: ignore
            
            return makeResponse(
                2003,
                None
            ) , 401



        # 判断是否为管理员页面
        if route_data["isAdmin"]: # type: ignore
            
            # 管理员页面，判断用户是否有权限
            if not token_info["user"]["isAdmin"] == True: # type: ignore
                # 非管理员用户，记录日志
                logger.warning(
                    {
                        "path": request.path,
                        "userId": token_info["user"]["id"], # type: ignore
                        "ip": getClientIp(),
                    },  "NonAdminUserAccess"
                )
                return makeResponse( # type: ignore
                2002,
                None
            ), 401
            
        
        # 继续请求
        g.user_info = result.data

def _handle_args():
    logger = extensions.getLogContext(extensions.logger, "BeforeRequest")

    if not extensions.routeManager.hasArguments(request.path):
        return None
    
    
    body = request.get_json()

    result, data = extensions.routeManager.validateArguments(request.path, body)

    if result:
        g.args = data
        # print(g.args)
        return None
    
    else:
        error_info = []
        for key, value in data.items():
            error_info.append({
                "key": key,
                "error": value.__class__.__name__,
                "msg": value.msg
            })

        # 失败
        
        return makeResponse(
            1001,
            error_info
        ), 400

def _handle_request_info():
    g.requestId = str(uuid.uuid4())

    g.logger = RequestLogContext(extensions.logger, "Request")

    g.startTime = time.time()


    try:
        responses = extensions.routeManager.routes[request.path]["responses"]
    except KeyError: 
        responses = {}

    g.res = ResponseGenerator(responses)

    getDatabase()

    return None

def before_request():
    # 请求前的逻辑
    handlers = [
        _handle_request_info,
        _handle_auth,
        _handle_args,
        
    ]

    for handler in handlers:
        result = handler()
        if result is not None:
            return result
        
    return None
