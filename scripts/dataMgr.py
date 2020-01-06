from baseHttpHandler import BaseHttpHandler
import json
import sqlite3
from enums import playerDataDBName
import dbMgr
import time
from threading import Timer
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
        elif(requestType == "commit"):
            commitDic = bodyDic["commitBody"]
            dataMgr.commitData(playerId,commitDic)
            message = {"type": "commitSuccess"}
        if (message):
            print(f"dataMgr: message is {message}")
            self.write(message)
            self.flush()
            self.finish()
    

class DataMgr(object):
    def __init__(self):
        super().__init__()
        self.playerDatas = {}
        self.expireDatas = {}
        self.autoSavedInterval = 3600
        self.autoClearInterval = 1800
        self.expireInterval = 1800

    def getPlayerDataById(self,id):

        if self.playerDatas.get(str(id),None) != None:
            self.updateExpireData(id)
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
                self.updateExpireData(id)
                return playerData
    
    def creatOnePlayerData(self,id):
        playerInitDic = None
        with open("../configs/playerInitData.json") as f:
            playerInitDic = json.load(f)[0]

        playerInitDic["id"] = id
        dbMgr.insertOneRecordToTableByOneDic(playerInitDic,playerDataDBName,"user")
        
        return playerInitDic

    def commitData(self,playerId,commitBody):
        playerData = self.getPlayerDataById(playerId)
        for k,v in commitBody.items():
            for key, value in playerData.items():
                if (k == key):
                    if (k == "id" or k == "playerId"):
                        continue
                    playerData[key] = commitBody[k]
                    break
        
        self.playerDatas[str(playerId)] = playerData
        self.updateExpireData(self,id)

    def savePlayerDatasToDB(self):
        dbMgr.writeRecordsToTableByOneDic(self.playerDatas,playerDataDBName,"user","id")
        
    def clearUnusedPlayerData(self):
        keysForClear = []
        for k,v in self.expireDatas.items():
            currentTime = time.time()
            if (currentTime >= v):
                keysForClear.append(k)
        
        if (len(keysForClear) > 0):
            playerDataDicForClear = {}
            for oneKey in keysForClear:
                playerDataDicForClear[oneKey] = self.playerDatas[oneKey]
                
            dbMgr.writeRecordsToTableByOneDic(playerDataDicForClear,playerDataDBName,"user","id")

            for oneKey in keysForClear:
                self.playerDatas.pop(oneKey)
                self.expireDatas.pop(oneKey)
            

    def updateExpireData(self,playerId):
        self.expireDatas[str(playerId)] = time.time() + self.expireInterval

    def startAutoSavePlayerDataToDB(self):
        def temp(self):
            self.savePlayerDatasToDB(self)
            t = Timer(self.autoSavedInterval,temp,[self])
            self._autoSaveTimer = t
            t.start()
        
        t = Timer(self.autoSavedInterval,temp,[self])
        self._autoSaveTimer = t
        t.start()
        

    def stopAutoSavePlayerDataToDB(self):
        if(self._autoSaveTimer):
            self._autoSaveTimer.cancel()
        
    
    def startAutoClearUnusedPlayerData(self):
        def temp(self):
            self.clearUnusedPlayerData(self)
            t = Timer(self.autoClearInterval,temp,[self])
            self._autoClearTimer = t
            t.start()
        
        t = Timer(self.autoSavedInterval,temp,[self])
        self._autoClearTimer = t
        t.start()        
        
    def stopAutoClearUnusedPlayerData(self):
        if (self._autoClearTimer):
            self._autoClearTimer.cancel()

dataMgr = DataMgr()
dataMgr.startAutoSavePlayerDataToDB()
dataMgr.startAutoClearUnusedPlayerData()
if __name__ == "__main__":
    pass