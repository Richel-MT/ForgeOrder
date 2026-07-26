from escpos.escpos import Escpos
from escpos.constants import QR_ECLEVEL_L, QR_ECLEVEL_M, QR_ECLEVEL_Q, QR_ECLEVEL_H

from .schema import QRCodeInfo

class Renderer:
    def __init__(self, printer: Escpos, qr_info: QRCodeInfo):
        self.printer = printer

        self.qr_info = qr_info

    def render(self, commands: list[dict]):
        for command in commands:
            self.render_command(command)

    def _text(self, cmd_info: dict):
        style = cmd_info["style"].copy()

        if "font" in style:
            style["font"] = style["font"].lower()

        if "scale" in style:
            style["width"] = style["scale"][0]
            style["height"] = style["scale"][1]
            del style["scale"]

            style["custom_size"] = True
        
        self.printer.set(**style)

        if cmd_info["newline"]:
            self.printer.textln(cmd_info["text"])
        else:
            self.printer.text(cmd_info["text"])

    def _qr(self, cmd_info: dict):
        content = cmd_info["content"]

        args = cmd_info
        del args["content"]

        args = args | self.qr_info

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
        

    def render_command(self, command: dict):
        match command["type"]:
            case "text":
                self._text(command["value"])
            case "qr_code":
                self._qr(command["value"])
