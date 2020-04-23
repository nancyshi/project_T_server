from baseHttpHandler import BaseHttpHandler
import json
import sqlite3
from enums import playerDataDBName
import dbMgr
import time
from threading import Timer
import datetime
import refreshSystem
import mailSystem

class DataMgrHandler(BaseHttpHandler):
    def post(self):
        body = self.request.body
        bodyDic = json.loads(body)
        playerId = bodyDic["playerId"]
        requestType = bodyDic["requestType"]
        message = None
        if (requestType == "query"):
            playerData = dataMgr.getPlayerDataById(playerId)
            dataMgr.resolveRefreshSystems(playerId)
            if (playerData):
                message = {"type": "success","playerData": playerData}
            else:
                message = {"type": "fail"}
        elif(requestType == "commit"):
            commitDic = bodyDic["commitBody"]
            playerData = dataMgr.getPlayerDataById(playerId)
            playerData = dataMgr.commitData(playerId,commitDic,playerData)
            message = {"type": "commitSuccess"}
        if (message):
            self.write(message)
            self.flush()
            self.finish()


class DataMgr(object):
    def __init__(self):
        super().__init__()
        self.playerDatas = {}
        self.expireDatas = {}
        self.autoSavedInterval = 60
        self.autoClearInterval = 100
        self.expireInterval = 1800

    def getPlayerDataById(self,id):
        playerDataForReturn = None
        if self.playerDatas.get(str(id),None) != None:
            playerDataForReturn = self.playerDatas[str(id)]

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
                    value = playerDataArry[index]
                    if isinstance(value,str):
                        try:
                            value = json.loads(value)
                        except ValueError:
                            pass

                    playerData[colNames[index]] = value

            if (len(playerData) > 0):
                playerDataForReturn = playerData
                self.playerDatas[str(id)] = playerData
        
        self.updateExpireData(id)
        return playerDataForReturn    
    
    def creatOnePlayerData(self,id):
        playerInitDic = None
        with open("../configs/playerInitData.json") as f:
            playerInitDic = json.load(f)[0]

        playerInitDic["id"] = id
        mailSystem.mailSystem.initMailSysData(playerInitDic)
        dbMgr.insertOneRecordToTableByOneDic(playerInitDic,playerDataDBName,"user")
        
        return playerInitDic

    def commitData(self,playerId,commitBody,playerData):
        # playerData = self.getPlayerDataById(playerId)
        # for k in commitBody:
        #     for key in playerData:
        #         if (k == key):
        #             if (k == "id" or k == "playerId"):
        #                 continue
        #             playerData[key] = commitBody[k]
        #             break
        for key, value in commitBody.items():
            if (type(value) is dict):
                self.commitData(playerId,value,playerData[key])
            else:
                if (key != "id" and key != "playerId"):
                    playerData[key] = value
        self.updateExpireData(playerId)
        return playerData

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
        def temp():
            self.savePlayerDatasToDB()
            t = Timer(self.autoSavedInterval,temp)
            self._autoSaveTimer = t
            t.start()
        
        t = Timer(self.autoSavedInterval,temp)
        self._autoSaveTimer = t
        t.start()
        

    def stopAutoSavePlayerDataToDB(self):
        if(self._autoSaveTimer):
            self._autoSaveTimer.cancel()
        
    
    def startAutoClearUnusedPlayerData(self):
        def temp():
            self.clearUnusedPlayerData()
            t = Timer(self.autoClearInterval,temp)
            self._autoClearTimer = t
            t.start()
        
        t = Timer(self.autoSavedInterval,temp)
        self._autoClearTimer = t
        t.start()        
        
    def stopAutoClearUnusedPlayerData(self):
        if (self._autoClearTimer):
            self._autoClearTimer.cancel()

    def resolveRefreshSystems(self,playerId):
        for s in refreshSystem.refreshSystemMgr.systems:
            s.resolveRefresh(playerId)

        

dataMgr = DataMgr()
dataMgr.startAutoSavePlayerDataToDB()
dataMgr.startAutoClearUnusedPlayerData()
if __name__ == "__main__":
    pass