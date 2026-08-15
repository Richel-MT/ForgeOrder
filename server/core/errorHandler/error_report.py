import datetime
from typing import Literal
import json
import sys
import os

from core.log.logger import Logger


def generateErrorReport(
    errorType: Literal["error", "critical"],
    errorTitle: str,
    errorDescription: str,
    errorDetail: str,
    time: datetime.datetime,
):
    
    
    errorFile = os.path.join(f"data/error_reports/{datetime.datetime.now().strftime("%Y-%m-%d")}.json")

    os.makedirs("data/error_reports", exist_ok=True)
    
    try:
        with open(errorFile, 'r', encoding='utf-8') as f:

        
            data = json.load(f)
            
    except json.JSONDecodeError:
            data = []

    except FileNotFoundError:
            data = []




    
    errorReport = {
        "id": len(data) + 1,
        "errorInfo": {
            "type": errorType,
            "title": errorTitle,
            "description": errorDescription,
            "detail": errorDetail,
            "time": time.isoformat(),
        },
        "sysInfo": {
            "os": sys.platform,
            "python": sys.version,  
        }
    }

    data.append(errorReport)

    with open(errorFile, 'w', encoding='utf-8') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=4))





    

    

    
