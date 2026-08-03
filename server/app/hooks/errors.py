import json

from flask import current_app, g
from werkzeug.exceptions import UnsupportedMediaType

from core.log.console import get_console_logger

from ..db.connections import close_database
import extensions
import traceback
from core.database.database.exceptions import DatabaseLockedError
from app.routes.schema import GLOBAL

# 415
def unsupported_media_type(e: UnsupportedMediaType):

        return GLOBAL.PAYLOAD_ERROR(e.description), 415
# 405
def method_not_allowed(e):
        return GLOBAL.METHOD_ERROR(), 405
    
# 404
def not_found(e):
        return GLOBAL.NOT_FOUND(), 404

# 500
def internal_server_error(e):
        return GLOBAL.SERVER_ERROR(), 500
    

# 数据库错误处理
def database_locked_error(e: DatabaseLockedError):
        g.logger.warning({
                "traceback": traceback.format_exception(type(e), e, e.__traceback__)
		}, "DatabaseBusy")
        return GLOBAL.DATABASE_BUSY(), 503

def database_error(e):
        return GLOBAL.DATABASE_ERROR(), 500

def teardown_appcontext(error):
	if error is not None:
			# 有错误，回滚事务
		if g.database is not None:
			g.database.rollback()

		logs = {
				"error": {
					"msg": str(error),
					"type": type(error).__name__,
				},
				"traceback": None
				
			}
		if isinstance(error, Exception):
			logs["traceback"] = traceback.format_exception(type(error), error, error.__traceback__) # type: ignore

		logger = get_console_logger("flask")

		logger.warning('\n'.join(traceback.format_exception(type(error), error, error.__traceback__))) # type: ignore
		extensions.logger.error(json.dumps(
			logs
		), "FLASK_APP", "RequestError")

	return current_app



def setup_error_handlers(app):
    app.errorhandler(405)(method_not_allowed)

    app.errorhandler(404)(not_found)
    app.errorhandler(500)(internal_server_error)
    app.errorhandler(415)(unsupported_media_type)

    app.errorhandler(DatabaseLockedError)(database_locked_error)

    app.teardown_appcontext(teardown_appcontext)