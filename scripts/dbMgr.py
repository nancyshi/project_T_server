import sqlite3
from enums import playerAccoutDBName
from enums import playerDataDBName
import json

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

def queryMathResultFromTable(identify,colName,dbName = playerAccoutDBName,tableName = "user"):
    accountDB = sqlite3.connect(dbName)
    cursor = accountDB.cursor()
    sqlCode = f"select * from {tableName} where {colName} = '{identify}'"
    cursor.execute(sqlCode)
    results = cursor.fetchall()
    cursor.close()
    accountDB.close()
    return results

def creatTableInDBByConfig(dbName, tableName, configPath,primaryKeyName):
    db = sqlite3.connect(dbName)
    cursor = db.cursor()

    sqlCode = f"create table {tableName} ("
    configDic = None
    with open(configPath) as f:
        configDic = json.load(f)[0]
    
    if configDic:
        index = 0
        for k in configDic.keys():
            valueType = type(configDic[k])
            temp = "text"
            strForAdd = None
            if (valueType == int):
                temp = "int"
            
            if k == primaryKeyName:
                strForAdd = f"{k} {temp} primary key"
            else:
                strForAdd = f"{k} {temp}"

            if index > 0 :
                strForAdd = f", " + strForAdd

            sqlCode = sqlCode + strForAdd
            index += 1

        sqlCode = sqlCode + ")"
        cursor.execute(sqlCode)
        cursor.close()
        db.commit()
        db.close()
        print (f"successly create {tableName} in {dbName}")
    else:
        print(f"fail to convert file {configPath} to dict")

def getColNamesFromTable(dbName, tableName, returnType= 1):
    """"return a dict or a arry
    Args:
        returnType: 1 = dict 2 = arry
    """
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    sqlCode = f"pragma table_info({tableName})"
    cursor.execute(sqlCode)

    results = cursor.fetchall()
    if (returnType == 1):

        colNames = {}
        for value in results:
            # a typical value is (0, 'id', 'int', 0, None, 1) , last para indicate whether it's a primary key
            colName = value[1]
            colType = value[2]
            colNames[colName] = colType
        
        return colNames
    if (returnType == 2):
        colNames = []
        for value in results:
            colNames.append(value[1])
        return colNames

def makeColsCorrect(dbName,tableName,configPath):
    dbColNames = getColNamesFromTable(dbName,tableName)
    configColNames = None
    with open(configPath) as f:
        configColNames = json.load(f)[0]

    colsNeedToAdd = {}
    for k,v in configColNames.items():
        flag = True
        for key, value in dbColNames.items():
            if (k == key):
                flag = False
                break
        if (flag == True):
            #need to add
            colsNeedToAdd[k] = type(v)

    # colsNeedToRemove = []
    # for k,v in dbColNames.items():
    #     flag = True
    #     for key,value in configColNames.items():
    #         if (k == key):
    #             flag = False
    #             break
    #     if (flag == True):
    #         colsNeedToRemove.append(k)
    if (len(colsNeedToAdd) > 0):
        db = sqlite3.connect(dbName)
        cursor = db.cursor()
        for k,v in colsNeedToAdd.items():
            colTypeForSQL = "text"
            if (v == int):
                colTypeForSQL = "int"
            defaultValue = configColNames[k]
            if (defaultValue == ""):
                defaultValue = "null"
            sqlCode = f"alter table {tableName} add {k} {colTypeForSQL} default '{defaultValue}'"
            cursor.execute(sqlCode)
            print (f"add one new col in {dbName}.{tableName}: {k}:{colTypeForSQL}")
        cursor.close()
        db.commit()
        db.close()
    else:
        print (f"{dbName}.{tableName}: data structure is ok")

def checkDataValid():
    if (checkTableExgist(playerAccoutDBName,"user") == False):
        creatTableInDBByConfig(playerAccoutDBName,"user","../configs/playerAccoutData.json","id")

    if (checkTableExgist(playerDataDBName, "user") == False):
        creatTableInDBByConfig(playerDataDBName,"user","../configs/playerInitData.json","id")

    makeColsCorrect(playerAccoutDBName,"user","../configs/playerAccoutData.json")
    makeColsCorrect(playerDataDBName,"user","../configs/playerInitData.json")

def insertOneRecordToTableByOneDic(dic,dbName,tableName):
    sqlCode = f"insert into {tableName} ("
    index = 0
    for k in dic.keys():
        strForAddToSql = f"{k}"
        if (index > 0):
            strForAddToSql = f", {k}"
        index += 1
        sqlCode = sqlCode + strForAddToSql
    sqlCode = sqlCode + f") values ("
    
    index = 0
    for v in dic.values():
        strForAddToSql = f"'{v}'"
        if (index > 0):
            strForAddToSql = f", '{v}'"
        index += 1
        sqlCode = sqlCode + strForAddToSql
    sqlCode = sqlCode + f")"
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    cursor.execute(sqlCode)
    cursor.close()
    db.commit()
    db.close()

def writeRecordsToTableByOneDic(dic,dbName,tableName,primaryKeyName):
    if (len(dic) == 0):
        return
    db = sqlite3.connect(dbName)
    cursor = db.cursor()

    for k, v in dic.items():
        sqlCode = f"update {tableName} set "
        index = 0
        for key, value in v.items():
            strForAdd = f"{key} = '{value}'"
            if index > 0:
                strForAdd = ", " + strForAdd
            sqlCode = sqlCode + strForAdd
            index += 1
        sqlCode = sqlCode + f" where {primaryKeyName} = '{k}'"
        cursor.execute(sqlCode)
    cursor.close()
    db.commit()
    db.close()

checkDataValid()
if __name__ == "__main__":
    pass
    