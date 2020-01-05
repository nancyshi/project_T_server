from baseHttpHandler import BaseHttpHandler
import json
import sqlite3
from enums import playerDataDBName
import dbMgr
import time
class DataMgrHandler(BaseHttpHandler):
    def post(self):
        print(f"DataMgrHandler: one connection from {self.request.remote_ip}, time: {time.time()}")
        body = self.request.body
        bodyDic = json.loads(body)
        playerId = bodyDic["playerId"]
        requestType = bodyDic["requestType"]
        message = None
        if (requestType == "query"):

            playerData = dataMgr.getPlayerDataById(playerId)
            if (playerData):
                message = {"type": "success","playerData": playerData}
            else:
                message = {"type": "fail"}
        
        if (message):
            print(f"dataMgr: message is {message}")
            self.write(message)
            self.flush()
            self.finish()
    

class DataMgr(object):
    def __init__(self):
        super().__init__()
        self.playerDatas = {}
        self.autoSavedInterval = 3600
        self.autoClearInterval = 1800

    def getPlayerDataById(self,id):

        if self.playerDatas.get(str(id),None) != None:
            return self.playerDatas[str(id)]

        else:
            results = dbMgr.queryMathResultFromTable(id,"id",playerDataDBName)
            playerData = None
            if len(results) == 0:
                playerData = self.creatOnePlayerData(id)
            else:
                playerDataArry = results[0]
                colNames = dbMgr.getColNamesFromTable(playerDataDBName,"user",2)
                playerData = {}
                for index in range(0,len(colNames)):
                    playerData[colNames[index]] = playerDataArry[index]

            if (len(playerData) > 0):
                self.playerDatas[str(id)] = playerData
                return playerData
    
    def creatOnePlayerData(self,id):
        playerInitDic = None
        with open("../configs/playerInitData.json") as f:
            playerInitDic = json.load(f)[0]

        playerInitDic["id"] = id
        dbMgr.insertOneRecordToTableByOneDic(playerInitDic,playerDataDBName,"user")
        
        return playerInitDic

    

dataMgr = DataMgr()