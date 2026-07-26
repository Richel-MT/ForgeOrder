
from typing import Literal, TypedDict


class QRCodeInfo(TypedDict):
    model: int
    native: bool
    correction: Literal["L", "M", "Q", "H"]