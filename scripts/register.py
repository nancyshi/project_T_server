import sqlite3
from enums import LoginCodeType
import json
from enums import playerAccoutDBName
import dbMgr

def registeOnePlayerByCode(code,codeType):
    playerAccoutInitDic = None
    with open("../configs/playerAccoutData.json") as f:
        playerAccoutInitDic = json.load(f)[0]
    db = sqlite3.connect(playerAccoutDBName)
    cursor = db.cursor()
    cursor.execute("select * from user")
    results = cursor.fetchall()
    
    playerId = playerAccoutInitDic["id"]
    if (len(results) > 0):
        lastResult = results[len(results) -1]
        playerId = lastResult[0] + 1
    
    sqlCode = None
    if (codeType == LoginCodeType.ACCOUT_AND_PASSWORD):
        temp = code.split("&&&",1)
        account = temp[0]
        password = temp[1]
        sqlCode = f"insert into user values ({playerId}, '{account}', '{password}', null, null)"
        
    elif (codeType == LoginCodeType.WECHAT_GAME):
        pass

    elif (codeType == LoginCodeType.DEVICE_ID):
        sqlCode = f"insert into user values ({playerId}, null, null, null, '{code}')"

    if (sqlCode != None):
        cursor.execute(sqlCode)
        cursor.close()
        db.commit()
        db.close()
        return playerId
