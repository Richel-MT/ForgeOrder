
class RepositoryError(Exception):
    '''数据库仓库错误'''
    pass

class TypeMismatchError(RepositoryError):
    '''列的类型与值类型不匹配'''

    def __init__(self, expected_type: type, got_type: type):
        super().__init__(
            f'Expect {expected_type}, but got {got_type}'
        )

class StringLengthError(RepositoryError):
    '''列的类型为String，长度错误'''

    def __init__(self, length: int, value: str):
        super().__init__(
            f'Expect string length <= {length}, but got {len(value)}'
        )

class InvalidJsonError(RepositoryError):
    '''列的类型为Json，JSON字符串无效'''

    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error

        super().__init__(
            f'Invalid JSON: {origin_error}'
        )

class ColumnNotFoundError(RepositoryError):
    '''列名不存在'''

    def __init__(self, column_name: str):
        super().__init__(
            f'Column {column_name} not found'
        )

class EmptyQueryCriteriaError(RepositoryError):
    '''查询参数缺失'''

    def __init__(self):
        super().__init__(
            f'Missing query criteria.'
        )
