import time

from flask import g, Response


def after_request(response: Response):
    g.endTime = time.time()

    cost: float = (g.endTime - g.startTime) * 1000 # 转换为毫秒

    g.logger.info({
        "status": response.status_code,
        "size": response.content_length, #bytes
        "duration": round(cost, 2), #ms
    }, "ResponseInfo")

    if cost > 500:
        g.logger.warning('', "TooSlowRequest")

    return response
