import json

from .commands import CommandBuilder, Command, Text, QRCode
    

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

        for command in self.commands:
            match command:
                case Text():

                    diff_style = {}

                    current_style = command.get_style()

                    # print(current_style)

                    if last_style is None:
                        # print("first text")
                        last_style = current_style.copy()

                        diff_style = current_style

                    else:
                        
                        diff_style_keys = [k for k in current_style if current_style[k] != last_style[k]]


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
                        "value": {
                            "content": command.content,
                            "size": command.size,
                        }
                    })

        return json.dumps(receipt_info, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    receipt = Receipt()

    receipt.build.text("text1", "B", align="left")
    receipt.build.text("text2", align="right")
    receipt.build.qr_code("https://www.baidu.com")

    print(receipt.render_json())
        
