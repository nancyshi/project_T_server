import refreshSystem
from dataMgr import dataMgr
from baseHttpHandler import BaseHttpHandler
import json

class SignInSysHandler(BaseHttpHandler):
    def post(self):
        body = self.request.body
        bodyDic = json.loads(body)
        playerId = bodyDic["playerId"]
        message = {}
        if bodyDic.get("signType",None) != None:
            signType = bodyDic["signType"]
            phy, heart = signInSys.signIn(signType,playerId)
            if phy != None :
                message["type"] = "success"
                message["physicalPower"] = phy
                message["heart"] = heart
            
            else:
                message["type"] = "fail"
            
        else:
            refreshDelta, refreshed = signInSys.resolveRefresh(playerId)
            if refreshed == True:
                message["type"] = "success"
                message["signInRefreshDelta"] = refreshDelta
            else:
                message["type"] = "fail"
                message["signInRefreshDelta"] = refreshDelta

        self.write(message)
        self.flush()
        self.finish()

class SignInSys(refreshSystem.RefreshSystem):
    def __init__(self):
        super().__init__()
        self.refreshTimeHour = 5
        self.refreshTimeMinute = 0
        self.refreshTimeSecond = 0
        self.physicalPowerAddNum = 10
        self.heartAddNum = 20
        self.addRateForAd = 2

    def onRefresh(self,playerId):
        playerData = dataMgr.getPlayerDataById(playerId)
        playerData["signInStatus"] = 1

    def resolveRefresh(self,playerId):
        refreshDelta, refreshed = super().resolveRefresh(playerId)
        playerData = dataMgr.getPlayerDataById(playerId)
        playerData["signInRefreshDelta"] = refreshDelta
        return (refreshDelta,refreshed)

    def signIn(self,givenType,playerId):
        playerData = dataMgr.getPlayerDataById(playerId)
        if givenType == 1:
            playerData["signInStatus"] = 2
            playerData["physicalPower"] += self.physicalPowerAddNum
            playerData["heart"] += self.heartAddNum
        elif givenType == 2:
            playerData["signInStatus"] = 3
            playerData["physicalPower"] += self.addRateForAd * self.physicalPowerAddNum
            playerData["heart"] += self.addRateForAd * self.heartAddNum
        
        elif givenType == 3:
            playerData["signInStatus"] = 3
            playerData["physicalPower"] += (self.addRateForAd - 1) * self.physicalPowerAddNum
            playerData["heart"] += (self.addRateForAd - 1) * self.heartAddNum
        
        else:
            return (None,None)

        return (playerData["physicalPower"], playerData["heart"])

signInSys = SignInSys()
refreshSystem.refreshSystemMgr.systems.append(signInSys)