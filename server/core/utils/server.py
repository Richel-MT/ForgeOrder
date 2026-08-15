from flask import jsonify, request
# from schema import Args
import os
import socket


# def verify_args(args: dict, args_format: list[Args]):
#     '''
#     验证参数是否符合要求
#     '''
#     args_invalid = []
#     for arg in args_format:
#         if arg["required"] and arg["arg_name"] not in args:
#             args_invalid.append(arg["arg_name"])
    
#     return args_invalid
      
def makeResponse(status: int, data: dict | list | int | str | bool | None, message: str = ""):
    return jsonify({
        "status": status,
        "data": data,
        "message": message
    })

def getClientIp():
    env = os.environ.get("ENV", "product")
    if env == "dev":
        # 开发环境优先使用 X-Real-IP 头
        return request.headers.get("X-Real-IP", request.remote_addr)
    else:
        return request.remote_addr
    

def getLocalIp():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"