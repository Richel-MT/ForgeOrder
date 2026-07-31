from dataclasses import dataclass
from typing import Any
from core.utils.server import make_response

@dataclass
class ResponseInfo:
    status_code: int
    name: str
    data_type: type | None

    def __call__(self, data: Any = None):
        return make_response(self.status_code, data)

class ResponseGenerator:
    def __init__(self, responses: list[ResponseInfo]):
        self.responses = responses

    def __getattr__(self, name):
        for resp in self.responses:
            if resp.name == name:
                return resp
            
        raise AttributeError(name)

    