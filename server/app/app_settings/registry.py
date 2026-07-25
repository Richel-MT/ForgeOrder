from re import U

from core.validation.field import FieldDefinition
from core.validation.validators import Choices, Interval, NotEmpty, Closed


SETTINGS = [
    FieldDefinition("shop.name", str, "ForgeOrder", NotEmpty()),


    FieldDefinition("printer.connection.type", str, "Network", Choices("Network", "Usb", "Win32Raw")),
    FieldDefinition("printer.connection.network.ip", str, "192.168.1.100", NotEmpty()),
    FieldDefinition("printer.connection.network.port", int, 9100, Interval(Closed(1), Closed(65535))),
    FieldDefinition("printer.connection.network.timeout", int, 10, Interval(0, None)),

    FieldDefinition("printer.connection.usb.vid", str, "0x000", NotEmpty()),
    FieldDefinition("printer.connection.usb.pid", str, "0x000", NotEmpty()),

    FieldDefinition("printer.connection.win32.name", str, "NAME", NotEmpty()),


    FieldDefinition("printer.encoding", str, "UTF-8", NotEmpty()),
    FieldDefinition("printer.text.fontSupport", bool, False), # 是否支持字体切换

    FieldDefinition("printer.QRCode.model", int, 1, Choices(1, 2, 3)), # 二维码模式，1是QR Code Model1，2是QR Code Model2，3是Micro QR Code （仅支持部分打印机）
    FieldDefinition("printer.QRCode.native", bool, False), # 是打印机生成qrcode还是escpos库生成
    FieldDefinition("printer.QRCode.correction", str, "L", Choices("L", "M", "Q", "H")), # 错误纠正等级


]
