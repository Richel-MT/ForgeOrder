import sqlite3


class DatabaseError(Exception):
    '''数据库连接基类'''
    originError: Exception = None #type: ignore

    def __init__(self, msg: str, originError: Exception = None): #type: ignore
        self.originError = originError

        super().__init__(msg)


class NotConnectedError(DatabaseError):
    '''数据库未连接异常'''

    def __init__(self):
        super().__init__("Database not connected or closed.")


class DatabaseLockedError(DatabaseError):
    '''数据库锁定异常'''

    def __init__(self, originError: Exception):
        self.originError = originError

        super().__init__("Database is locked.")

class ConstraintError(DatabaseError):
    '''约束错误基类'''  
class UniqueConstraintError(ConstraintError):
    '''唯一(UNIQUE)约束错误'''

    def __init__(self, originError: Exception):
        self.originError = originError

        super().__init__("Unique constraint error. " + str(originError))
class ForeignKeyConstraintError(ConstraintError):
    '''外键约束错误'''

    def __init__(self, originError: Exception):
        self.originError = originError

        super().__init__("Foreign key constraint error. " + str(originError))
class PrimaryKeyConstraintError(ConstraintError):
    '''主键约束错误'''

    def __init__(self, originError: Exception):
        self.originError = originError

        super().__init__("Primary key constraint error. " + str(originError))
class NotNullConstraintError(ConstraintError):
    '''非空约束错误'''

    def __init__(self, originError: Exception):
        self.originError = originError

        super().__init__("Not null constraint error. " + str(originError))
class CheckConstraintError(ConstraintError):
    '''检查约束错误'''

    def __init__(self, originError: Exception):
        self.originError = originError

        super().__init__("Check constraint error. " + str(originError))

class DatabaseCannotOpenError(DatabaseError):
    '''数据库无法打开错误'''

    def __init__(self, msg: str, originError: Exception = None): #type: ignore
        self.originError = originError

        super().__init__(msg, originError)


class DatabaseTypeError(DatabaseError):
    def __init__(self, originError: Exception):
        self.originError = originError

        super().__init__("type mismatch. " + str(originError))


def getBasicCode(code: int):
    '''获取SQLite错误码的基本码'''
    return code & 0xff

def convertError(error: sqlite3.Error):
    '''转换数据库错误'''

    sqliteErrorcode = getattr(error, "sqlite_errorcode", None)
    sqliteErrorname = getattr(error, "sqlite_errorname", None)

    if sqliteErrorcode is None:
        return  DatabaseError("Unknown database error. " + str(error), error)

    match sqliteErrorcode:
        case 5:
            return DatabaseLockedError(error)
        case 2067:
            return UniqueConstraintError(error)
        case 1555:
            return PrimaryKeyConstraintError(error)
        case 787:
            return ForeignKeyConstraintError(error)
        case 1299:
            return NotNullConstraintError(error)
        case 279:
            return CheckConstraintError(error)
        # case 14:
        #     raise DatabaseFileError("Cannot open database file. ", error)
        # case 26:
        #     raise DatabaseFileError("File is not a database.", error)
        # case 13:
        #     raise DatabaseFileError("Disk is full.", error)

        case 20:
            return DatabaseTypeError(error)
        
        case _:
            basicCode = getBasicCode(sqliteErrorcode)

            match basicCode:
                case 14:
                    return DatabaseCannotOpenError(f"({sqliteErrorcode} {sqliteErrorname}) Cannot open database file. ", error)
                case _:
                    return DatabaseError(f"({basicCode} {sqliteErrorcode} {sqliteErrorname}) Unknown database error. " + str(error), error)

        
