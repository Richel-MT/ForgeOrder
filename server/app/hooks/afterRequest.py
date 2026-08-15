import time

from flask import g, Response


def afterRequest(response: Response):
    g.endTime = time.time()

    cost: float = (g.endTime - g.startTime) * 1000 # 转换为毫秒

    g.logger.setCategory("Request")

    logInfo = {
        "httpStatus": response.status_code,
        # "actionStatus": response.json["status"],
        # "actionMessage": response.json["message"],
        "size": response.content_length, #bytes
        "duration": round(cost, 2), #ms
    }

    if response.json:
        logInfo["actionStatus"] = response.json["status"]
        logInfo["actionMessage"] = response.json["message"]

    g.logger.info(logInfo, "ResponseInfo")

    if cost > 500:
        g.logger.warning('', "TooSlowRequest")

    return response
