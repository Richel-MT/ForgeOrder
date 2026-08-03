import json
from typing import Any

from . import Service
from .schema import SETTINGS
from .exceptions import *
from core.type_convert import TypeConverterManager, TypeConvertError


converter = TypeConverterManager()

converter.register_converter(str, int, int)
converter.register_converter(int, str, str)

converter.register_converter(str, bool, lambda x: x == "1")
converter.register_converter(bool, str, lambda x: "1" if x else "0")

converter.register_converter(str, list, lambda x: json.loads(x))
converter.register_converter(list, str, lambda x: json.dumps(x))

converter.register_converter(str, dict, lambda x: json.loads(x))
converter.register_converter(dict, str, lambda x: json.dumps(x))

class SettingsService(Service):

    def _init(self):
        for prop in SETTINGS:

            row = self.repo_manager.settings.get(key=prop.key)

            if row is None:
                # 不存在则创建
                self.repo_manager.settings.insert(
                    key=prop.key,
                    value=prop.default
                )
                continue
            else:
                # 验证设置项是否有效
                
                # 转换类型
                try:
                    value = converter.convert(row["value"], prop.value_type)
                except TypeConvertError:
                    raise SettingsInitError(f"类型转换错误，{row["value"]}不能转换为{prop.value_type}。")
                
                if prop.validator:
                    result = prop.validator.validate(value, self)


                    if not result.success:
                        raise SettingsInitError(f"AppSettings错误。{prop.key}验证失败，{result.error}")

    def get(self, key: str):
        
        prop = next((prop for prop in SETTINGS if prop.key == key), None)
        
        if prop is None:
            raise SettingNotFoundError(key)
        
        row = self.repo_manager.settings.get(key=key)

        if row is None:
            return prop.default

        try:
            return converter.convert(row["value"], prop.value_type) # 可能抛出TypeConvertError
        
        except TypeConvertError:
            raise SettingTypingError(key, prop.value_type, type(row["value"]))

    def set(self, key: str, value: Any):
        prop = next((prop for prop in SETTINGS if prop.key == key), None)
        
        if prop is None:
            raise SettingNotFoundError(key)
        
        if not isinstance(value, prop.value_type):
            raise SettingTypingError(key, prop.value_type, type(value))
        
        value_str = converter.convert(value, prop.value_type)
        
        self.repo_manager.settings.update(
            where={"key": key},
            data={"value": value_str}
        )