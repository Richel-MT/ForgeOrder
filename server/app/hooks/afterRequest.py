import time

from flask import g, Response


def afterRequest(response: Response):
    g.endTime = time.time()

    cost: float = (g.endTime - g.startTime) * 1000 # 转换为毫秒

    g.logger.setCategory("Request")

    g.logger.info({
        "httpStatus": response.status_code,
        "actionStatus": response.json["status"],
        "actionMessage": response.json["message"],
        "size": response.content_length, #bytes
        "duration": round(cost, 2), #ms
    }, "ResponseInfo")

    if cost > 500:
        g.logger.warning('', "TooSlowRequest")

    return response
