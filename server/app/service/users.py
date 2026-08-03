
import secrets
from datetime import datetime, timedelta
from enum import Enum, auto

from werkzeug.security import check_password_hash

from core.config.json_config import JSONConfig
from . import Service, Result
from ..db.respository import RepositoryManager

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




class UserService(Service):
    LOGIN = LoginResult
    LOGOUT = LogoutResult
    AUTH = AuthResult

    def _generate_token(self):
        return secrets.token_urlsafe(32)

    def _insert_token(self, user_id: int, token: str, expire_time: datetime, ip: str):
        self.repo_manager.tokens.insert(
            user_id=user_id,
            token=token,
            status=0,
            expire_time=expire_time,
            ip=ip,
        )

    
    def __init__(self, repo_manager: RepositoryManager, config: JSONConfig):
        super().__init__(repo_manager)

        self.available_time = config.get("auth.available_time")


    def login(self, username: str, password: str, ip: str, cover: bool):
        '''
        用户登录操作。
        '''

        users = self.repo_manager.users.get(username=username)

        if users is None:
            # 用户不存在
            return Result(self.LOGIN.USERNAME_OR_PASSWORD_ERROR)

        # 判断密码是否正确
        if not check_password_hash(users["password"], password):
            # 密码错误
            return Result(self.LOGIN.USERNAME_OR_PASSWORD_ERROR)
        
        # 检查用户是否启用
        if not users["is_available"]:
            # 用户未启用
            return Result(self.LOGIN.USER_DISABLED)
        
        # 检查token是否存在
        token = self.repo_manager.tokens.get(user_id=users["id"])

        if token is None:
            # token不存在，生成新的token
            token = self._generate_token()
            expire_time = datetime.now() + timedelta(days=self.available_time)

            self._insert_token(users["id"], token, expire_time, ip)

        else:
            # token存在


            # 判断是否有效
            if token["status"] != 0 or token["expire_time"] < datetime.now():
                # token无效
                # 删除旧token
                self.repo_manager.tokens.update(
                    where={"id": token["id"]},
                    data={"status": 3}
                )
        
            # 判断ip是否匹配，token是否过期，token是否已注销
            if token["ip"] != ip:
                # token有效
                if not cover:
                    return Result(self.LOGIN.NEW_DEVICE, {
                        "old_device": token["ip"]
                    })
                else:
                    # 删除旧token
                    self.repo_manager.tokens.update(
                        where={"id": token["id"]},
                        data={"status": 3}
                    )

                    # 生成新的token
                    token = self._generate_token()
                    expire_time = datetime.now() + timedelta(days=self.available_time)

                    self.repo_manager.tokens.insert(
                        user_id=users["id"],
                        token=token,
                        status=0,
                        expire_time=expire_time,
                        ip=ip,
                    )

            else:
                # ip相同，同一设备的重复登录
                return Result(self.LOGIN.REPEAT_LOGIN)
            
            
        # 删除敏感信息
        user_info = users.copy()
        del user_info["password"]

        # 更新users表中的last_login_at
        self.repo_manager.users.update(
            where={"id": users["id"]},
            data={"last_login_at": datetime.now()}
        )

        self.repo_manager.users.commit()
        # 返回结果
        return Result(self.LOGIN.SUCCESS, {
            "token": token,
            "user": user_info,
        })

    def logout(self, token: str):
        '''
        用户退出登录操作。
        '''


        # 检查token是否存在
        token_info = self.repo_manager.tokens.get(token=token)
        if token_info is None:
            # token不存在
            return Result(self.LOGOUT.TOKEN_INVALID)

        # 更新token表中的status为2
        self.repo_manager.tokens.update(
            where={"token": token},
            data={"status": 2}
        )

        # 整体提交事务
        self.repo_manager.tokens.commit()

        # 返回结果
        return Result(self.LOGOUT.SUCCESS, token_info)

    def check_token(self, token: str):
        '''
        检查token是否有效。
        '''

        token_info = self.repo_manager.tokens.get(token=token)

        if token_info is None:
            # token不存在
            return Result(self.AUTH.TOKEN_INVALID)

        if token_info["status"] != 0:
            # token无效，删除
            self.repo_manager.tokens.delete(
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
        if now > token_info["expire_time"]:
            # token已过期，更新数据库信息
            self.repo_manager.tokens.update(
                where={"token": token},
                data={"status": 1}
            )

            self.repo_manager.tokens.commit()
            return Result(self.AUTH.TOKEN_EXPIRED)
            
        else:
            # token未过期，更新过期时间
            self.repo_manager.tokens.update(
                where={"token": token},
                data={"expire_time": now + timedelta(days=self.available_time)}
            )


        self.repo_manager.tokens.commit()

        # 获取用户信息
        user_info = self.repo_manager.users.get(id=token_info["user_id"])

        token_info["user"] = user_info
        return Result(self.AUTH.SUCCESS, token_info)
