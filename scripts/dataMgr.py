from baseHttpHandler import BaseHttpHandler
import json
import sqlite3
from enums import playerDataDBName
import dbMgr
import time
from threading import Timer
import datetime

class DataMgrHandler(BaseHttpHandler):
    def post(self):
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
            playerData = dataMgr.commitData(playerId,commitDic)
            message = {"type": "commitSuccess","refreshDelta": playerData["refreshDelta"]}
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
        self.refreshTimeHour = 3
        self.refreshTimeMinute = 2
        self.refreshTimeSecond = 0

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
                    playerData[colNames[index]] = playerDataArry[index]

            if (len(playerData) > 0):
                playerDataForReturn = playerData

        self.resolveRefresh(playerDataForReturn)
        return playerDataForReturn    
    
    def creatOnePlayerData(self,id):
        playerInitDic = None
        with open("../configs/playerInitData.json") as f:
            playerInitDic = json.load(f)[0]

        playerInitDic["id"] = id
        dbMgr.insertOneRecordToTableByOneDic(playerInitDic,playerDataDBName,"user")
        
        return playerInitDic

    def commitData(self,playerId,commitBody):
        playerData = self.getPlayerDataById(playerId)
        self.resolveRefresh(playerData)
        for k,v in commitBody.items():
            for key, value in playerData.items():
                if (k == key):
                    if (k == "id" or k == "playerId"):
                        continue
                    playerData[key] = commitBody[k]
                    break
        
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

    def resolveRefresh(self,playerData):
        lastInteractTime = playerData["lastInteractTime"]
        currentTime = time.time()
        if lastInteractTime != 0:
            formatLastInteractTime = time.localtime(lastInteractTime)
            year = formatLastInteractTime.tm_year
            month = formatLastInteractTime.tm_mon
            day = formatLastInteractTime.tm_mday

            tmpRefreshTime = datetime.datetime(year,month,day,self.refreshTimeHour,self.refreshTimeMinute,self.refreshTimeSecond)
            tmpRefreshTime = tmpRefreshTime.timetuple()
            tmpRefreshTime = time.mktime(tmpRefreshTime)
            if tmpRefreshTime < lastInteractTime:
                tmpRefreshTime = tmpRefreshTime + 24 * 60 * 60
            
            if currentTime >= tmpRefreshTime:
                playerData["physicalPower"] = playerData["maxPhysicalPower"]
                playerData["heart"] = playerData["maxHeart"]

        playerData["lastInteractTime"] = currentTime
        formatCurrentTime = time.localtime(currentTime)
        y = formatCurrentTime.tm_year
        m = formatCurrentTime.tm_mon
        d = formatCurrentTime.tm_mday
        targetRefreshTime = datetime.datetime(y,m,d,self.refreshTimeHour,self.refreshTimeMinute,self.refreshTimeSecond)
        targetRefreshTime = targetRefreshTime.timetuple()
        targetRefreshTime = time.mktime(targetRefreshTime)
        if targetRefreshTime < currentTime:
            targetRefreshTime = targetRefreshTime + 24 * 60 * 60
        
        refreshDelta = targetRefreshTime - currentTime
        playerData["refreshDelta"] = refreshDelta
        id = playerData["id"]
        self.playerDatas[str(id)] = playerData
        self.updateExpireData(id)
        return playerData
        

dataMgr = DataMgr()
dataMgr.startAutoSavePlayerDataToDB()
dataMgr.startAutoClearUnusedPlayerData()
if __name__ == "__main__":
    pass