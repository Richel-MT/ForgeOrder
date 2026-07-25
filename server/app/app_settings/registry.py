from re import U

from core.validation.field import FieldDefinition
from core.validation.validators import Choices, NotEmpty


SETTINGS = [
    FieldDefinition("shop.name", str, "ForgeOrder", NotEmpty()),


    FieldDefinition("printer.encoding", str, "UTF-8", NotEmpty()),

    FieldDefinition("printer.QRCode.model", int, 1, Choices(1, 2, 3)), # 二维码模式，1是QR Code Model1，2是QR Code Model2，3是Micro QR Code （仅支持部分打印机）
    FieldDefinition("printer.QRCode.native", bool, False), # 是打印机生成qrcode还是escpos库生成
    FieldDefinition("printer.QRCode.correction", str, "L", Choices("L", "M", "Q", "H")), # 错误纠正等级


]
