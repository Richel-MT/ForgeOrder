from dataclasses import dataclass
from decimal import DivisionImpossible
from typing import Literal

class Command:
    pass

@dataclass
class Text(Command):
    text: str

    font: Literal["a", "b"] = 'a'
    align: Literal["left", "center", "right"] = 'left'
    bold: bool  = False
    underline: int = 0 #0:无下划线 #1:但下划线
    scale: tuple[int, int] = (1, 1) # 缩放，width，height
    invert: bool = False

    newLine: bool = True

    def getStyle(self):
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
    center: bool = False

    def toDict(self):
        return {
            "content": self.content,
            "size": self.size,
            "center": self.center,
        }


@dataclass
class Divider(Command):
    pass



class Row:
    def __init__(self, *contents, divider: bool = False):
        self.contents: list[str] = list(contents)

        self.divider: bool = divider

    def toDict(self):
        return {
            "contents": self.contents,
            "divider": self.divider,
        }

class Column:
    def __init__(self, width: int, spacing: int = 1):
        self.width: int = width
        self.spacing: int = spacing

    def toDict(self):
        return {
            "width": self.width,
            "spacing": self.spacing,
        }
    
@dataclass 
class Table(Command):
    def __init__(self, columns: list[Column], rows: list[Row]):
        self.columns: list[Column] = columns
        self.rows: list[Row] = rows


    def toDict(self):

        return {
            "columns": [column.toDict() for column in self.columns],
            "rows": [row.toDict() for row in self.rows],
        }




class CommandBuilder:


    def __init__(self, receipt: 'Receipt') -> None:
        self.receipt = receipt

    def text(self,
             text: str,
            font: Literal["a", "b"] = "a",
            align: Literal["left", "center", "right"] = "left",
            bold: bool = False,
            underline: int = 0, #0:无下划线 #1:但下划线
            scale: tuple[int, int] = (1, 1), # 缩放，width，height
            invert: bool = False,
            newLine: bool = True,
             ):
        textCommand = Text(text, font, align, bold, underline, scale, invert, newLine)

        self.receipt.add(textCommand)

        return textCommand

    def qrCode(self,
                 content: str,
                 size: int = 3,
                 center: bool = False
                 ):
        qrCodeCommand = QRCode(content, size, center)

        self.receipt.add(qrCodeCommand)

        return qrCodeCommand

    def divider(self):
        divider = Divider()

        self.receipt.add(divider)

        return divider

    def table(self,
               columns: list[Column],
               rows: list[Row],
               ):
        table = Table(columns, rows)

        self.receipt.add(table)

        return table
