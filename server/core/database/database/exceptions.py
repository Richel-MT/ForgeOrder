import sqlite3

from core.db.database import Database

class DatabaseError(Exception):
    '''数据库连接基类'''
    origin_error: Exception = None #type: ignore

    def __init__(self, msg: str, origin_error: Exception = None): #type: ignore
        self.origin_error = origin_error

        super().__init__(msg)


class NotConnectedError(DatabaseError):
    '''数据库未连接异常'''

    def __init__(self):
        super().__init__("Database not connected or closed.")


class DatabaseLockedError(DatabaseError):
    '''数据库锁定异常'''

    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error

        super().__init__("Database is locked.")

class ConstraintError(DatabaseError):
    '''约束错误基类'''  
class UniqueConstraintError(ConstraintError):
    '''唯一(UNIQUE)约束错误'''

    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error

        super().__init__("Unique constraint error. " + str(origin_error))
class ForeignKeyConstraintError(ConstraintError):
    '''外键约束错误'''

    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error

        super().__init__("Foreign key constraint error. " + str(origin_error))
class PrimaryKeyConstraintError(ConstraintError):
    '''主键约束错误'''

    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error

        super().__init__("Primary key constraint error. " + str(origin_error))
class NotNullConstraintError(ConstraintError):
    '''非空约束错误'''

    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error

        super().__init__("Not null constraint error. " + str(origin_error))
class CheckConstraintError(ConstraintError):
    '''检查约束错误'''

    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error

        super().__init__("Check constraint error. " + str(origin_error))

class DatabaseCannotOpenError(DatabaseError):
    '''数据库无法打开错误'''

    def __init__(self, msg: str, origin_error: Exception = None): #type: ignore
        self.origin_error = origin_error

        super().__init__(msg, origin_error)


class DatabaseTypeError(DatabaseError):
    def __init__(self, origin_error: Exception):
        self.origin_error = origin_error

        super().__init__("type mismatch. " + str(origin_error))


def get_basic_code(code: int):
    '''获取SQLite错误码的基本码'''
    return code & 0xff

def convert_error(error: sqlite3.Error):
    '''转换数据库错误'''

    sqlite_errorcode = getattr(error, "sqlite_errorcode", None)
    sqlite_errorname = getattr(error, "sqlite_errorname", None)

    if sqlite_errorcode is None:
        return  DatabaseError("Unknown database error. " + str(error), error)

    match sqlite_errorcode:
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
            basic_code = get_basic_code(sqlite_errorcode)

            match basic_code:
                case 14:
                    return DatabaseCannotOpenError(f"({sqlite_errorcode} {sqlite_errorname}) Cannot open database file. ", error)
                case _:
                    return DatabaseError(f"({basic_code} {sqlite_errorcode} {sqlite_errorname}) Unknown database error. " + str(error), error)

        
