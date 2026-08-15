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

class PrintTaskService(Service):
    CREATE = CreateResult
    UPDATE = UpdateResult


    def create(self, content: Receipt, context: dict = {}):
        '''
        创建打印任务。
        '''
        task_id = str(uuid.uuid7())

        content_str = content.renderJSON()

        context_str = json.dumps(context)

        create_time = datetime.datetime.now()

        self.repositoryManager.printTask.insert(
            id=task_id,

            content=content_str,
            context=context_str,
            created_at=create_time
        )

        self.repositoryManager.printTask.commit()

        return Result(self.CREATE.SUCCESS, task_id)

    def update(self, task_id: str, status: int, err_message: str | None= None):
        '''
        更新打印任务状态。
        '''

        update_time = datetime.datetime.now()

        if status == 2 or status == 3: # 成功或者出错了
            finish_time = update_time
        else:
            finish_time = None

        try:
            self.repositoryManager.printTask.update(
                where={"id": task_id},
                data={
                    "status": status,
                    "err_message": err_message,
                    "finish_time": finish_time,
                    "updated_at": update_time
                }
            )
        except RecordNotFoundError:
            return Result(self.UPDATE.TASK_NOT_FOUND)
        
        self.repositoryManager.printTask.commit()
        
        return Result(self.UPDATE.SUCCESS)
