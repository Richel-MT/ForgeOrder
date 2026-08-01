import uuid
import time

from flask import request, g

from app.routes.exceptions import ArgumentException
import extensions
from core.utils.server import make_response, get_client_ip
from app.log import RequestLogContext
from app.routes.res_generator import ResponseGenerator

def _handle_auth():
    # 获取日志上下文
    logger = g.logger.get_log_context("BEFORE_REQUEST")

    if  request.path.startswith("/api/"):
        check_result, route_data = extensions.route_manager.verify_auth(request.path)
        
        if not check_result:
            # 路由不存在
            return make_response(
                1003,
                None
            ), 404
        

        if not route_data["auth"]: #type: ignore
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
        return make_response(
            2001,
            None
        ), 401
    
    elif token.startswith("Bearer "):
        # Token格式正确
        token = token.split(" ")[1] # 提取token部分
    else:
        # Token格式错误
        return make_response(
            2003,
            None
        ), 401

    # 使用AuthManager验证Token
    status, result = extensions.auth_manager.verify(token)
    
    
    if not status:
        # 验证失败，处理错误
        match result:
            case None:
                # Token无效
                logger.info({
                    "ip": get_client_ip(),
                    "error": "InvalidToken"
                }, "AuthError")

                return make_response(
                    2003,
                    None
                ) , 401
            case "expire":
                # Token过期
                logger.info({
                    "ip": get_client_ip(),
                    "error": "TokenExpire"
                }, "AuthError")
                

                return make_response(
                    2004,
                    None
                ) , 401
            case "logout":
                # 用户已退出登录
                logger.info({
                    "ip": get_client_ip(),
                    "error": "TokenLogout"
                }, "AuthError")
                # 用户退出登录
                return make_response(
                    2003,
                    None
                ) , 401
            case "old_device":
                # 旧设备登录
                logger.info({
                    "ip": get_client_ip(),
                    "error": "OldDevice"
                }, "AuthError")

                return make_response(
                    2005,
                    None
                ) , 401
    else:
        # Token有效

        # 判断Token记录的ip与请求的ip是否一致
        if result["device_ip"] != get_client_ip(): # type: ignore
            # ip不一致
            logger.info({
                "ip": get_client_ip(),
                "token_ip": result["device_ip"],
                "error": "IPNotMatch"
            }, "AuthError") # type: ignore
            
            return make_response(
                2003,
                None
            ) , 401
        else:
            # ip一致
            pass
            
        # 用户认证成功，更新Token到期时间
        extensions.auth_manager.update_time(token)


        # 判断是否为管理员页面
        if route_data["is_admin"]: # type: ignore
            
            # 管理员页面，判断用户是否有权限
            if not result["user"]["is_admin"] == 1: # type: ignore
                # 非管理员用户，记录日志
                logger.warning(
                    {
                        "path": request.path,
                        "user_id": result["user"]["id"], # type: ignore
                        "ip": get_client_ip(),
                    },  "NonAdminUserAccess"
                )
                return make_response( # type: ignore
                2002,
                None
            ), 401
            
        
        # 继续请求
        g.user_info = result

def _handle_args():
    logger = extensions.get_log_context(extensions.logger, "BEFORE_REQUEST")

    if not extensions.route_manager.has_args(request.path):
        logger.debug("请求路径 %s，无需验证参数" % request.path, "DebugMsg")
        return None
    
    
    body = request.get_json()

    result, data = extensions.route_manager.validate_args(request.path, body)

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
        
        return make_response(
            1001,
            error_info
        ), 400

def _handle_request_info():
    g.request_id = str(uuid.uuid4())

    
    g.logger = RequestLogContext(extensions.logger, "REQUEST")

    g.start_time = time.time()


    try:
        responses = extensions.route_manager.routes[request.path]["responses"]
    except KeyError: 
        responses = {}

    g.res = ResponseGenerator(responses)

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
