import sqlite3
from enum import Enum
from enums import LoginCodeType

def getPlayerIdByCode(code,codeType):
    if (codeType == LoginCodeType.ACCOUT_AND_PASSWORD):
        temp = code.split("&&&")
        account = temp[0]
        password = temp[1]
        accountDB = sqlite3.connect("playerAccout.db")
        cursor = accountDB.cursor()
        cursor.execute("select * from user where accout = ?" , (account,))
        values = cursor.fetchall()

        if (values.count >= 1):
            oneValue = values[0]
            playerId = oneValue[0]
            password_db = oneValue[2]
            if (password_db == password):
                cursor.close()
                accountDB.close()
                return playerId

            else:
                pass

    elif (codeType == LoginCodeType.WECHAT_GAME):
        pass

    elif (codeType == LoginCodeType.DEVICE_ID):
        pass

    
