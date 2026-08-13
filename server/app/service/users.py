
import secrets
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import cast 
from werkzeug.security import check_password_hash, generate_password_hash

from core.config.json_config import JSONConfig
from .base import Service, Result
from ..db.respository import RepositoryManager
from core.database.repository.exceptions import RecordNotFoundError

class LoginResult(Enum):
    SUCCESS = auto()
    USERNAME_OR_PASSWORD_ERROR = auto()
    USER_DISABLED = auto()
    NEW_DEVICE = auto()
    REPEAT_LOGIN = auto()

class LogoutResult(Enum):
    SUCCESS = auto()
    TOKEN_INVALID = auto()

class AuthResult(Enum):
    SUCCESS = auto()
    TOKEN_INVALID = auto()

    TOKEN_EXPIRED = auto()
    TOKEN_LOGOUT = auto()
    TOKEN_OLD_DEVICE = auto()

class UserResult(Enum):
    SUCCESS = auto()

    MISSING_QUERY = auto() # 缺失查询条件

    USER_NOT_FOUND = auto()

    OLD_PASSWORD_ERROR = auto() # 再更改密码操作中，旧密码错误



class UserService(Service):
    LOGIN = LoginResult
    LOGOUT = LogoutResult
    AUTH = AuthResult
    USER = UserResult

    def _generate_token(self):
        '''使用secrets库生成随机token'''
        return secrets.token_urlsafe(32)

    def _insert_token(self, user_id: int, token: str, expire_time: datetime, ip: str):
        '''
        将一条token插入到表中。
        '''
        self.repositoryManager.tokens.insert(
            userId=user_id,
            token=token,
            status=0,
            expireTime=expire_time,
            ip=ip,
        )

    
    def __init__(self, repo_manager: RepositoryManager, config: JSONConfig | None = None):
        super().__init__(repo_manager)


        if config is None:
            from extensions import config
        
        self.available_time = config.get("auth.available_time")

        


    def login(self, username: str, password: str, ip: str, cover: bool):
        '''
        用户登录操作。
        '''

        repeat_login = False

        users = self.repositoryManager.users.get(username=username)

        if users is None:
            # 用户不存在
            return Result(self.LOGIN.USERNAME_OR_PASSWORD_ERROR)

        # 判断密码是否正确
        if not check_password_hash(users["password"], password):
            # 密码错误
            return Result(self.LOGIN.USERNAME_OR_PASSWORD_ERROR)
        
        # 检查用户是否启用
        if not users["isAvailable"]:
            # 用户未启用
            return Result(self.LOGIN.USER_DISABLED)
        
        # 检查token是否存在
        token_info = self.repositoryManager.tokens.get(userId=users["id"])

        if token_info is None:
            # token不存在，生成新的token
            token = self._generate_token()
            expire_time = datetime.now() + timedelta(days=self.available_time)

            self._insert_token(users["id"], token, expire_time, ip)
            

        else:
            # token存在
            token = token_info["token"]

            # 判断是否有效
            if token_info["status"] != 0 or token_info["expireTime"] < datetime.now():
                # token无效
                # 删除旧token
                self.repositoryManager.tokens.update(
                    where={"id": token_info["id"]},
                    data={"status": 3}
                )

                # 生成新的token
                token = self._generate_token()
                expire_time = datetime.now() + timedelta(days=self.available_time)

                self._insert_token(users["id"], token, expire_time, ip)
        
                
            if token_info["ip"] != ip:
                # token有效
                if not cover:
                    return Result(self.LOGIN.NEW_DEVICE, {
                        "old_device": token_info["ip"]
                    })
                else:
                    # 删除旧token
                    self.repositoryManager.tokens.update(
                        where={"id": token_info["id"]},
                        data={"status": 3}
                    )

                    # 生成新的token
                    token = self._generate_token()
                    expire_time = datetime.now() + timedelta(days=self.available_time)

                    self.repositoryManager.tokens.insert(
                        user_id=users["id"],
                        token=token,
                        status=0,
                        expire_time=expire_time,
                        ip=ip,
                    )

            else:
                # ip相同，同一设备的重复登录
                repeat_login = True

            
                           
            
        # 删除敏感信息
        user_info = dict(users.copy())
        del user_info["password"]

        # 更新users表中的last_login_at
        self.repositoryManager.users.update(
            where={"id": users["id"]},
            data={"lastLoginAt": datetime.now()}
        )

        self.repositoryManager.users.commit()
        # 返回结果


        return Result(self.LOGIN.SUCCESS if not repeat_login else self.LOGIN.REPEAT_LOGIN, {
            "token": token,
            "user": user_info,
        })

    def logout(self, token: str):
        '''
        用户退出登录操作。
        '''


        # 检查token是否存在
        token_info = self.repositoryManager.tokens.get(token=token)
        if token_info is None:
            # token不存在
            return Result(self.LOGOUT.TOKEN_INVALID)

        # 更新token表中的status为2
        self.repositoryManager.tokens.update(
            where={"token": token},
            data={"status": 2}
        )

        # 整体提交事务
        self.repositoryManager.tokens.commit()

        # 返回结果
        return Result(self.LOGOUT.SUCCESS, token_info)

    def check_token(self, token: str):
        '''
        检查token是否有效。
        '''

        token_info = self.repositoryManager.tokens.get(token=token)

        if token_info is None:
            # token不存在
            return Result(self.AUTH.TOKEN_INVALID)

        if token_info["status"] != 0:
            # token无效，删除
            self.repositoryManager.tokens.delete(
                where={"id": token_info["id"]}
            )
        
        if token_info["status"] == 1:
            # token已过期
            return Result(self.AUTH.TOKEN_EXPIRED)
        elif token_info["status"] == 2:
            # token已退出登录
            return Result(self.AUTH.TOKEN_LOGOUT)
        elif token_info["status"] == 3:
            # token旧设备
            return Result(self.AUTH.TOKEN_OLD_DEVICE)

        # 检查过期时间
        now = datetime.now()
        if now > token_info["expireTime"]:
            # token已过期，更新数据库信息
            self.repositoryManager.tokens.update(
                where={"token": token},
                data={"status": 1}
            )

            self.repositoryManager.tokens.commit()
            return Result(self.AUTH.TOKEN_EXPIRED)
            
        else:
            # token未过期，更新过期时间
            self.repositoryManager.tokens.update(
                where={"token": token},
                data={"expireTime": now + timedelta(minutes=self.available_time)}
            )


        self.repositoryManager.tokens.commit()

        # 获取用户信息
        user_info = self.repositoryManager.users.get(id=token_info["userId"])

        token_info = dict(token_info)
        token_info["user"] = user_info
        return Result(self.AUTH.SUCCESS, token_info)


    def get(self, user_id: int | None = None, username: str | None = None):
        '''
        通过id或用户名获取用户信息。
        '''

        if user_id:
            result = self.repositoryManager.users.get(id=user_id)
        elif username:
            result = self.repositoryManager.users.get(username=username)
        else:
            return Result(self.USER.MISSING_QUERY)

        if result is None:
            return Result(self.USER.USER_NOT_FOUND)

        return Result(self.USER.SUCCESS, result)


    def change_password_force(self, user_id: int, new_password: str):
        '''
        强制更改用户的密码。

        注意：本方法直接更改用户的密码，在一般场景，请勿使用。
        '''

        
        password_hash = generate_password_hash(new_password)

        try:
            self.repositoryManager.users.update(
                where={"id": user_id},
                data={"password": password_hash}
            )
        except RecordNotFoundError:
            return Result(self.USER.USER_NOT_FOUND)

        return Result(self.USER.SUCCESS)
        
    def change_password(self, user_id: int, old_password: str, new_password: str):
        '''
        更改用户的密码。

        传入用户id、旧密码（明文）、新密码（明文）。
        '''

        status, user = self.get(user_id=user_id)
        
        if status != self.USER.SUCCESS:
            return Result(status)

        user = cast(dict, user)

    
        if not check_password_hash(user["password"], old_password):
            # 旧密码错误
            return Result(self.USER.OLD_PASSWORD_ERROR)

        # 旧密码正确

        self.change_password_force(user_id, new_password)

        return Result(self.USER.SUCCESS)

        
    def create(self,
                username: str,
                password: str,
                is_admin: bool,
                is_available: bool,
                ):

        create_time = datetime.now()

        password_hash = generate_password_hash(password)

        user_id = self.repositoryManager.users.insert(
            username=username,
            password=password_hash,
            isAdmin=is_admin,
            isAvailable=is_available,
            createdAt=create_time,
        )

        self.repositoryManager.users.commit()

        return Result(self.USER.SUCCESS, user_id)

    


