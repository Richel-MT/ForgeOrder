import json

from .commands import CommandBuilder, Command, Text, QRCode, Divider, Table
    

class Receipt:
    def __init__(self):
        self.commands = []

        self.build = CommandBuilder(self)

    def add(self, command: Command):
        self.commands.append(command)


    def render_json(self):
        receipt_info = {
            "version": 1,
            "commands": []
        }

        last_style = None

        full_style = None

        for command in self.commands:
            match command:
                case Text():
                    
                    
                    diff_style = {}

                    current_style = command.get_style()

                    if full_style is None:
                        full_style = current_style.copy()

                    if last_style is None:
                        last_style = current_style.copy()

                        diff_style = current_style

                    else:
                        
                        diff_style_keys = [k for k in current_style if current_style[k] != last_style[k]]

                        full_style.update(current_style)

                        for key in diff_style_keys:
                            last_style[key] = current_style[key]
                            diff_style[key] = current_style[key]

                    # print(diff_style)   

                    receipt_info["commands"].append({
                        "type": "text",
                        "value": {
                            "text": command.text,
                            "newline": command.new_line,
                            "style": diff_style
                        }
                    })

                    # print(receipt_info["commands"])

                    # print("---- ")

                case QRCode():
                    receipt_info["commands"].append({
                        "type": "qr_code",
                        "value": command.to_dict()
                    })

                case Divider():
                    if full_style is None:
                        font = "a"
                    else:
                        font = full_style["font"]

                    if full_style is not None:
                        width = full_style["scale"][0]
                    else:
                        width = 1
                    
                    receipt_info["commands"].append({
                        "type": "divider",
                        "value": {
                            "font": font,
                            "width": width
                        }
                    })

                case Table():
                    if full_style is None:
                        font = "a"
                    else:
                        font = full_style["font"]

                    if full_style is not None:
                        width = full_style["scale"][0]
                    else:
                        width = 1


                    receipt_info["commands"].append({
                        "type": "table",
                        "value": {
                            "font": font,
                            "width": width,
                            "value": command.to_dict(),
                        }
                        
                    })


        return json.dumps(receipt_info, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    receipt = Receipt()

    receipt.build.text("text1", "b", align="left")
    receipt.build.text("text2", align="right")
    receipt.build.text("text2", align="left", underline=1)
    receipt.build.qr_code("https://www.baidu.com")

    receipt.render_json()
        
