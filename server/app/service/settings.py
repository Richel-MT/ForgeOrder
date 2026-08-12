import json
from typing import Any

from .base import Service
from .schema import SETTINGS
from .exceptions import *
from core.typeConvert import converter, TypeConvertError




class SettingsService(Service):

    def _init(self):
        '''
        初始化设置项。
        '''
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
        '''
        获取设置项的值。
        '''
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
        '''
        设置设置项的值。
        '''
        prop = next((prop for prop in SETTINGS if prop.key == key), None)
        
        if prop is None:
            raise SettingNotFoundError(key)
        
        if not isinstance(value, prop.value_type):
            raise SettingTypingError(key, prop.value_type, type(value))
        
        value_str = converter.convert(value, str)
        
        self.repo_manager.settings.update(
            where={"key": key},
            data={"value": value_str}
        )