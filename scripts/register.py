import sqlite3
from enums import LoginCodeType
import json
from enums import playerAccoutDBName

def registeOnePlayerByCode(code,codeType):
    if (checkTableExgist(playerAccoutDBName,"user") == False):
        creatAccoutUserTable()
    if (codeType == LoginCodeType.ACCOUT_AND_PASSWORD):
        with open("../configs/playerAccoutData.json") as f:
            playerAccoutInitDic = json.loads(f)
            temp = code.split("&&&",1)
            accout = temp[0]
            password = temp[1]
            db = sqlite3.connect(playerAccoutDBName)
            cursor = db.cursor()
            cursor.execute("select * from user")
            results = cursor.fetchall()
            
            if (results.count == 0):
                sqlCode = f"insert into user values ({playerAccoutInitDic[id]}, {accout}, {password}, null, null)"
                cursor.execute(sqlCode)
                cursor.close()
                db.commit()
                db.close()
                return playerAccoutInitDic[id]
            else:
                lastResult = results[results.count -1]
                playerId = lastResult[0] + 1
                sqlCode = f"insert into user values ({playerId}, {accout}, {password}, null, null)"
                cursor.execute(sqlCode)
                cursor.close()
                db.commit()
                db.close()
                return playerId
    elif (codeType == LoginCodeType.WECHAT_GAME):
        return -1

    elif (codeType == LoginCodeType.DEVICE_ID):
        return -1


def checkTableExgist(dbName,tableName):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    sqlCode = "select " + tableName + " from sqlite_master where type = ?"
    cursor.execute(sqlCode,("table",))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    if (results.count > 0 ):
        return True
    else:
        return False


def creatAccoutUserTable():
    db = sqlite3.connect(playerAccoutDBName)
    cursor = db.cursor()
    cursor.execute("create table user (id int primary key, accout text, password text, wechatOpenId text, deviceId text)")
    cursor.close()
    db.commit()
    db.close()

