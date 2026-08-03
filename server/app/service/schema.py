
from core.validation.field import FieldDefinition
from core.validation.validators import Choices, Interval, NotEmpty, Closed, If
from core.validation.condition import RefIs


SETTINGS = [
    FieldDefinition("shop.name", str, "ForgeOrder", NotEmpty()),

    FieldDefinition("shop.isBusiness", bool, False), # 是否是营业状态

    FieldDefinition("printer.enabled", bool, False), # 是否启用打印机

    FieldDefinition("printer.connection.type", str, "", 
                    If(RefIs("printer.enabled", True),Choices("Network", "Usb", "Win32Raw",))),

    FieldDefinition("printer.connection.network.ip", str, "",
                     If(RefIs("printer.connection.type", "Network"), NotEmpty())),

    FieldDefinition("printer.connection.network.port", int, 9100, 
                     If(RefIs("printer.connection.type", "Network"),Interval(Closed(1), Closed(65535)))
                     ),
    FieldDefinition("printer.connection.network.timeout", int, 10, 
                     If(RefIs("printer.connection.type", "Network"),Interval(0, None))),

    FieldDefinition("printer.connection.usb.vid", int, 0, 
                     If(RefIs("printer.connection.type", "Usb"),NotEmpty())),

    FieldDefinition("printer.connection.usb.pid", int, 0, 
                     If(RefIs("printer.connection.type", "Usb"),NotEmpty())),

    FieldDefinition("printer.connection.win32.name", str, "", 
                     If(RefIs("printer.connection.type", "Win32Raw"),NotEmpty())),


    FieldDefinition("printer.encoding", str, "UTF-8", NotEmpty()),

    FieldDefinition("printer.profile", str, "Generic", NotEmpty()),
    FieldDefinition("printer.dotsPerLine", int, 576, Interval(1, None)),  # 每行像素数

    FieldDefinition("printer.QRCode.model", int, 2, Choices(1, 2, 3)), # 二维码模式，1是QR Code Model1，2是QR Code Model2，3是Micro QR Code （仅支持部分打印机）
    FieldDefinition("printer.QRCode.native", bool, False), # 是打印机生成qrcode还是escpos库生成
    FieldDefinition("printer.QRCode.correction", str, "Q", Choices("L", "M", "Q", "H")), # 错误纠正等级
]
