
class RepositoryError(Exception):
    '''数据库仓库错误'''
    pass

class TypeMismatchError(RepositoryError):
    '''列的类型与值类型不匹配'''

    def __init__(self, expectedType: type, gotType: type):
        super().__init__(
            f'Expect {expectedType}, but got {gotType}'
        )

class StringLengthError(RepositoryError):
    '''列的类型为String，长度错误'''

    def __init__(self, length: int, value: str):
        super().__init__(
            f'Expect string length <= {length}, but got {len(value)}'
        )

class InvalidJsonError(RepositoryError):
    '''列的类型为Json，JSON字符串无效'''

    def __init__(self, originError: Exception):
        self.originError = originError

        super().__init__(
            f'Invalid JSON: {originError}'
        )

class ColumnNotFoundError(RepositoryError):
    '''列名不存在'''

    def __init__(self, columnName: str):
        super().__init__(
            f'Column {columnName} not found'
        )

class EmptyQueryCriteriaError(RepositoryError):
    '''查询参数缺失'''

    def __init__(self):
        super().__init__(
            f'Missing query criteria.'
        )

class RecordNotFoundError(RepositoryError):
    '''记录不存在'''

    def __init__(self, where: dict):
        super().__init__(
            f'Record not found: {where}'
        )
