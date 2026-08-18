import time

from flask import Response

from app.utils import g


def afterRequest(response: Response):
    g.endTime = time.time()

    cost: float = (g.endTime - g.startTime) * 1000 # 转换为毫秒

    g.logger.setCategory("Request")

    logInfo = {
        "httpStatus": response.status_code,
        "size": response.content_length, #bytes
        "duration": round(cost, 2), #ms
    }


    g.logger.info(logInfo, "ResponseInfo")

    if response.json:
        if not response.json.get("status") and not response.json.get("message"):
            raise ValueError(f"Response is invalid.")
        else:
            if response.json["status"] != 0:
                g.logger.warning({
                                "status": response.json["status"],
                                "message": response.json["message"],
                }, "ResponseStatusError")

    if cost > 500:
        g.logger.warning('', "TooSlowRequest")

    return response
