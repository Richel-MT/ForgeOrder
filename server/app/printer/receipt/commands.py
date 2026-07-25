from dataclasses import dataclass
from typing import Literal

class Command:
    pass

@dataclass
class Text(Command):
    text: str

    font: Literal["A", "B"] = 'A'
    align: Literal["left", "center", "right"] = 'left'
    bold: bool  = False
    underline: int = 0 #0:无下划线 #1:但下划线
    scale: tuple[int, int] = (1, 1) # 缩放，width，height
    invert: bool = False

    new_line: bool = True

    def get_style(self):
        # print(self)
        return {
            "font": self.font,
            "align": self.align,
            "bold": self.bold,
            "underline": self.underline,
            "scale": self.scale,
            "invert": self.invert,
        }.copy()


@dataclass
class QRCode(Command):
    content: str

    size: int = 3 # 二维码大小




class CommandBuilder:


    def __init__(self, receipt: 'Receipt') -> None:
        self.receipt = receipt

    def text(self,
             text: str,
            font: Literal["A", "B"] = "A",
            align: Literal["left", "center", "right"] = "left",
            bold: bool = False,
            underline: int = 0, #0:无下划线 #1:但下划线
            scale: tuple[int, int] = (1, 1), # 缩放，width，height
            invert: bool = False,
            new_line: bool = True,
             ):
        text_command = Text(text, font, align, bold, underline, scale, invert, new_line)

        self.receipt.add(text_command)

        return text_command

    def qr_code(self,
                 content: str,
                 size: int = 3,
                 ):
        qr_code_command = QRCode(content, size)

        self.receipt.add(qr_code_command)

        return qr_code_command
