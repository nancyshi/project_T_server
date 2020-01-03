import sqlite3
from enums import playerAccoutDBName

def checkTableExgist(dbName,tableName):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    
    sqlCode = f"select tbl_name from sqlite_master where type = ?"
    cursor.execute(sqlCode,("table",))
    results = cursor.fetchall()
    cursor.close()
    db.close()
    if (len(results) > 0 ):
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

def queryMathResultFromUserTable(identify,colName):
    accountDB = sqlite3.connect(playerAccoutDBName)
    cursor = accountDB.cursor()
    sqlCode = f"select * from user where {colName} = '{identify}'"
    cursor.execute(sqlCode)
    results = cursor.fetchall()
    return results


if (checkTableExgist(playerAccoutDBName,"user") == False):
    creatAccoutUserTable()

