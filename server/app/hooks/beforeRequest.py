import uuid
import time

from flask import request, g

from app.db.connections import getDatabase
from app.service.users import UserService
from app.routes import routeManager
from core.utils.server import getClientIp
from core.log import getLogger
from app.log import RequestLogContext
from app.routes.responseGenerator import ResponseGenerator
from app.routes.schema import GLOBAL

def _handleAuth():
    # 获取日志上下文
    logger = g.logger.getLogContext("Auth")

    if  request.path.startswith("/api/"):
        checkResult, routeData = routeManager.getAuthConfig(request.path)
        
        if not checkResult:
            # 路由不存在
            return GLOBAL.NOT_FOUND(), 404
        

        if not routeData["requiresAuth"]: #type: ignore
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
        return GLOBAL.TOKEN_INVALID_ERROR(), 401
    
    elif token.startswith("Bearer ") and len(token.split(" ")) > 1:
        # Token格式正确
        token = token.split(" ")[1] # 提取token部分
    else:
        # Token格式错误
        return GLOBAL.TOKEN_INVALID_ERROR(), 401

    # 使用UserService验证Token
    service = UserService(g.repos)

    result = service.checkToken(token)
    
    if result.code != service.AUTH.SUCCESS:
        # 验证失败，处理错误
        match result.code:
            case service.AUTH.TOKEN_INVALID:
                # Token无效
                logger.warning({
                    "ip": getClientIp(),
                    "error": "InvalidToken"
                }, "AuthError")

                return GLOBAL.TOKEN_INVALID_ERROR(), 401
            
            case service.AUTH.TOKEN_EXPIRED:
                # Token过期
                logger.warning({
                    "ip": getClientIp(),
                    "error": "TokenExpire"
                }, "AuthError")
                

                return GLOBAL.TOKEN_EXPIRED_ERROR(), 401
            
            case service.AUTH.TOKEN_LOGOUT:
                # 用户已退出登录
                logger.warning({
                    "ip": getClientIp(),
                    "error": "TokenLogout"
                }, "AuthError")
                # 用户退出登录

                return GLOBAL.TOKEN_INVALID_ERROR(), 401
            
            case service.AUTH.TOKEN_OLD_DEVICE:
                # 旧设备登录
                logger.warning({
                    "ip": getClientIp(),
                    "error": "OldDevice"
                }, "AuthError")

                return GLOBAL.OLD_DEVICE_TOKEN(), 401
    else:
        # Token有效

        # 判断Token记录的ip与请求的ip是否一致
        tokenInfo: dict = result.data #type: ignore
        if tokenInfo["ip"] != getClientIp(): # type: ignore
            # ip不一致
            logger.warning({
                "ip": getClientIp(),
                "tokenIp": tokenInfo["ip"],
                "error": "IPNotMatch"
            }, "AuthError") # type: ignore
            
            return GLOBAL.TOKEN_INVALID_ERROR(), 401



        # 判断是否为管理员页面
        if routeData["isAdmin"]: # type: ignore
            
            # 管理员页面，判断用户是否有权限
            if not tokenInfo["user"]["isAdmin"] == True: # type: ignore
                # 非管理员用户，记录日志
                logger.warning(
                    {
                        "path": request.path,
                        "userId": tokenInfo["user"]["id"], # type: ignore
                        "ip": getClientIp(),
                    },  "NonAdminUserAccess"
                )
                return GLOBAL.PERMISSION_ERROR(), 401
            
        
        # 继续请求
        g.userInfo = result.data["user"] #type: ignore

def _handleArguments():
    logger = g.logger.getLogContext("RequestArguments")

    if not routeManager.hasArguments(request.path):
        return None
    
    
    body = request.get_json()

    result, data = routeManager.validateArguments(request.path, body)

    if result:
        g.args = data
        # print(g.args)
        return None
    
    else:
        errorInfo = []
        for key, value in data.items():
            errorInfo.append({
                "key": key,
                "error": value.__class__.__name__,
                "msg": value.msg
            })

        # 失败
        logger.info(errorInfo, "ArgumentsError")

        return GLOBAL.ARGUMNET_ERROR(errorInfo), 400

def _handleRequestInfo():
    g.requestId = str(uuid.uuid4())
    
    g.logger = RequestLogContext(getLogger(), "BeforeRequest")

    g.startTime = time.time()

    g.logger.info({
        "requestId": g.requestId,
        "ip": request.remote_addr,
        "path": request.path,
        "method": request.method,
    }, "RequestInfo", g.requestId)


    try:
        responses = routeManager.routes[request.path]["responses"]
    except KeyError: 
        responses = {}

    g.res = ResponseGenerator(responses) #type: ignore

    getDatabase()

    return None

def beforeRequest():
    # 请求前的逻辑
    handlers = [
        _handleRequestInfo,
        _handleAuth,
        _handleArguments,
        
    ]

    for handler in handlers:
        result = handler()
        if result is not None:
            return result
        
    return None
