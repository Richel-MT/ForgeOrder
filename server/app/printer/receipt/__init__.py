import json

from .commands import CommandBuilder, Command, Text, QRCode, Divider, Table
    

class Receipt:
    def __init__(self):
        self.commands = []

        self.build = CommandBuilder(self)

    def add(self, command: Command):
        self.commands.append(command)


    def renderJSON(self):
        receiptInfo = {
            "version": 1,
            "commands": []
        }

        lastStyle = None

        fullStyle = None

        for command in self.commands:
            match command:
                case Text():
                    
                    
                    diffStyle = {}

                    currentStyle = command.getStyle()

                    if fullStyle is None:
                        fullStyle = currentStyle.copy()

                    if lastStyle is None:
                        lastStyle = currentStyle.copy()

                        diffStyle = currentStyle

                    else:
                        
                        diffStyleKeys = [k for k in currentStyle if currentStyle[k] != lastStyle[k]]

                        fullStyle.update(currentStyle)

                        for key in diffStyleKeys:
                            lastStyle[key] = currentStyle[key]
                            diffStyle[key] = currentStyle[key]

                    # print(diff_style)   

                    receiptInfo["commands"].append({
                        "type": "text",
                        "value": {
                            "text": command.text,
                            "newline": command.newLine,
                            "style": diffStyle
                        }
                    })

                    # print(receipt_info["commands"])

                    # print("---- ")

                case QRCode():
                    receiptInfo["commands"].append({
                        "type": "qr_code",
                        "value": command.toDict()
                    })

                case Divider():
                    if fullStyle is None:
                        font = "a"
                    else:
                        font = fullStyle["font"]

                    if fullStyle is not None:
                        width = fullStyle["scale"][0]
                    else:
                        width = 1
                    
                    receiptInfo["commands"].append({
                        "type": "divider",
                        "value": {
                            "font": font,
                            "width": width
                        }
                    })

                case Table():
                    if fullStyle is None:
                        font = "a"
                    else:
                        font = fullStyle["font"]

                    if fullStyle is not None:
                        width = fullStyle["scale"][0]
                    else:
                        width = 1


                    receiptInfo["commands"].append({
                        "type": "table",
                        "value": {
                            "font": font,
                            "width": width,
                            "value": command.toDict(),
                        }
                        
                    })


        return json.dumps(receiptInfo, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    receipt = Receipt()

    receipt.build.text("text1", "b", align="left")
    receipt.build.text("text2", align="right")
    receipt.build.text("text2", align="left", underline=1)
    receipt.build.qrCode("https://www.baidu.com")

    receipt.renderJSON()
        
