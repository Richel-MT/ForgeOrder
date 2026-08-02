from werkzeug.security import check_password_hash

from . import Service, Result
from ..db.respository import RepositoryManager
import extensions

class UserService(Service):
    LOGIN_SUCCESS = 100
    LOGIN_USERNAME_OR_PASSWORD_ERROR = 101

    def __init__(self, repo_manager: RepositoryManager, ):

    def login(self, username: str, password: str):
        '''
        用户登录
        '''

        users = self.repo_manager.users.get(username=username)

        if users is None:
            # 用户不存在
            return Result(self.LOGIN_USERNAME_OR_PASSWORD_ERROR)

        # 判断密码是否正确
        if not check_password_hash(users["password"], password):
            # 密码错误
            return Result(self.LOGIN_USERNAME_OR_PASSWORD_ERROR)
        
        # 密码正确

        # 检查token是否存在
        token = self.repo_manager.tokens.get(user_id=users["id"])

        if token is None:
            # token不存在
            self.repo_manager.tokens.create(
                user_id=users["id"],
                token=self.generate_token(),
                status=0,
                expire_time=datetime.now() + timedelta(days=1),
                ip="",
            )


        
