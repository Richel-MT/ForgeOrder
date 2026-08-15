import unicodedata

from escpos.escpos import Escpos
from escpos.constants import QR_ECLEVEL_L, QR_ECLEVEL_M, QR_ECLEVEL_Q, QR_ECLEVEL_H

from .schema import QRCodeInfo
from ..receipt.schema import FONT_A_WIDTH, FONT_B_WIDTH, CH_WIDTH

def getCharWidth(font: str, scale: int = 1):
    if font == "a":
        return FONT_A_WIDTH * scale
    else:
        return FONT_B_WIDTH * scale

def lengthOfString(text: str, font: str, scale: int = 1):
    charWidth = getCharWidth(font, scale)

    length = 0
    for char in text:
        widthProperty = unicodedata.east_asian_width(char)

        if widthProperty in ('F', 'W'):
            length += CH_WIDTH * scale
        else:
            length += charWidth

    return length

def lengthToCharCount(length: int, font: str, scale: int = 1):
    charWidth = getCharWidth(font, scale)

    return length // charWidth

def getFirstChars(text: str, count: int, font: str, scale: int = 1):
    # print(text, count)

    textCount = 0
    finalText = ''

    for char in text:
        textCount += lengthOfString(char, font, scale)
        
        if textCount >= count:
            return finalText
        else:
            finalText += char

    return finalText

class Renderer:
    def __init__(self, printer: Escpos, qrInfo: QRCodeInfo):
        self.printer = printer

        self.qrInfo = qrInfo

    def render(self, commands: list[dict], dots: int):
        for command in commands:
            self.renderCommand(command, dots)

    def _text(self, commandInfo: dict):
        style = commandInfo["style"].copy()

        if "font" in style:
            style["font"] = style["font"].lower()

        if "scale" in style:
            style["width"] = style["scale"][0]
            style["height"] = style["scale"][1]
            del style["scale"]

            style["customSize"] = True
        
        self.printer.set(**style)

        if commandInfo["newline"]:
            self.printer.textln(commandInfo["text"])
        else:
            self.printer.text(commandInfo["text"])

    def _qr(self, commandInfo: dict):
        content = commandInfo["content"]

        args = commandInfo
        del args["content"]

        args = args | self.qrInfo

        ec = QR_ECLEVEL_L
        match args["correction"]:
            case "L":
                ec = QR_ECLEVEL_L
            case "M":
                ec = QR_ECLEVEL_M
            case "Q":
                ec = QR_ECLEVEL_Q
            case "H":
                ec = QR_ECLEVEL_H

        self.printer.qr(content,
                        size=args["size"],
                        model=args["model"],
                        native=args["native"],
                        ec=ec,
                        center=args["center"],
                        )

    def _divider(self, commandInfo: dict, dots: int):
        self.printer.set(font=commandInfo["font"])

        charWidth = FONT_A_WIDTH if commandInfo["font"] == "a" else FONT_B_WIDTH

        charWidth *= commandInfo["width"]

        charCount = dots // charWidth

        self.printer.textln("-" * charCount)

    def _table(self, commandInfo: dict, dots: int):
        columns = commandInfo["value"]["columns"]

        rows = commandInfo["value"]["rows"]

        for row in rows:
            contents = row["contents"]
            divider = row["divider"]

            remainText = ""

            for i, content in enumerate(contents):
                column = columns[i]

                length = lengthOfString(content, commandInfo["font"], commandInfo["width"])
                if  length > column["width"]:
                    text = getFirstChars(content, column["width"], commandInfo["font"], commandInfo["width"])

                    remainText = content[len(text):]

                    # print(text, remain_text)

                    self.printer.text(text)

                    textLength = lengthOfString(text, commandInfo["font"], commandInfo["width"])

                    self.printer.text(" " * (lengthToCharCount(column["width"] - textLength , commandInfo["font"], commandInfo["width"]) ))

                else:
                    text = content
                    self.printer.text(content)

                    self.printer.text(" " * (lengthToCharCount(column["width"] - length , commandInfo["font"], commandInfo["width"]) ))

            self.printer.textln()

            if remainText:
                self.printer.textln(remainText)

            if divider:
                self._divider({
                    "font": commandInfo["font"],
                    "width": commandInfo["width"],
                }, dots)



                

            

    def renderCommand(self, command: dict, dots: int):
        match command["type"]:
            case "text":
                self._text(command["value"])
            case "qr_code":
                self._qr(command["value"])

            case "divider":
                self._divider(command["value"], dots)

            case "table":
                self._table(command["value"], dots)

            
