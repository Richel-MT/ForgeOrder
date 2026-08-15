import uuid
import json
import datetime
from enum import Enum, auto
from app.printer.receipt import Receipt

from .base import Service, Result
from core.database.repository.exceptions import RecordNotFoundError

class CreateResult(Enum):
    SUCCESS = auto()

class UpdateResult(Enum):
    SUCCESS = auto()
    TASK_NOT_FOUND = auto()

class GetResult(Enum):
    SUCCESS = auto()
    TASK_NOT_FOUND = auto()

class PrintTaskService(Service):
    CREATE = CreateResult
    UPDATE = UpdateResult
    GET = GetResult

    def get(self, taskId: str):
        '''
        获取打印任务。
        '''
        try:
            rows = self.repositoryManager.printTask.get(id=taskId)
        except RecordNotFoundError:
            return Result(self.GET.TASK_NOT_FOUND)
        
        return Result(self.GET.SUCCESS, rows)
        
    def create(self, content: Receipt, context: dict = {}):
        '''
        创建打印任务。
        '''
        taskId = str(uuid.uuid7())

        contentString = content.renderJSON()


        contextString = json.dumps(context)

        createTime = datetime.datetime.now()

        self.repositoryManager.printTask.insert(
            id=taskId,

            content=contentString,
            context=contextString,
            createdAt=createTime
        )

        self.repositoryManager.printTask.commit()

        return Result(self.CREATE.SUCCESS, taskId)

    def update(self, taskId: str, status: int, errorMessage: str | None= None):
        '''
        更新打印任务状态。
        '''

        udpateTime = datetime.datetime.now()

        if status == 2 or status == 3: # 成功或者出错了
            finishedTime = udpateTime
        else:
            finishedTime = None

        try:
            self.repositoryManager.printTask.update(
                where={"id": taskId},
                data={
                    "status": status,
                    "errorMessage": errorMessage,
                    "finishedAt": finishedTime,
                    "updatedAt": udpateTime
                }
            )
        except RecordNotFoundError:
            return Result(self.UPDATE.TASK_NOT_FOUND)
        
        self.repositoryManager.printTask.commit()
        
        return Result(self.UPDATE.SUCCESS)
