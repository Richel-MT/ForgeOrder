import logging

maxNameLength = 0
maxLevelLength = 0

class Formatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        global maxLevelLength, maxNameLength

        if len(record.levelname) > maxLevelLength:
            maxLevelLength = len(record.levelname)

        record.levelname = record.levelname.lower().ljust(maxLevelLength)

        if len(record.name) > maxNameLength:
            maxNameLength = len(record.name)

        record.name = record.name.ljust(maxNameLength)

        record.reset = '\033[0m'


        match record.levelname.strip():
            case 'info':
                record.color = ''
                record.levelname = f'\033[34m{record.levelname}\033[0m'
            case 'warning':
                record.color = '\033[33m'
            case 'error':
                record.color = '\033[31m'
            case _:
                record.color = ''
            

        return super().format(record)



def getConsoleLogger(name: str) -> logging.Logger:

    logger = logging.getLogger(name)
    logger.propagate = False 

    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        consoleHandler = logging.StreamHandler()

        consoleHandler.setLevel(logging.INFO)
        formatter = Formatter("%(color)s%(name)s %(levelname)s %(message)s%(reset)s")
        consoleHandler.setFormatter(formatter)

        logger.addHandler(consoleHandler)

    return logger

