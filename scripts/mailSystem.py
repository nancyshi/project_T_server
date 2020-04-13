from baseHttpHandler import BaseHttpHandler
import dataMgr
import json
import time
from threading import Timer
import asyncio


class MailSystemHandler(BaseHttpHandler):
    async def post(self):
        body = self.request.body
        bodyDic = json.loads(body)
        playerId = bodyDic["playerId"]
        message = None
        mailId = bodyDic["mailId"]
        requestType = bodyDic["requestType"]
        if requestType == "readMail":
            index = bodyDic["selectedOptionIndex"]
            result = mailSystem.readOneMail(playerId,mailId,index)
            if result == True:
                message = {
                    "type": "success",
                }
            else:
                message = {
                    "type": "fail",
                    "reason": "player don't have this mail"
                }
        elif requestType == "sendMail":
            tag = bodyDic["tag"]
            delay = bodyDic["delay"]
            timeStamp = await mailSystem.sendOneMailToPlayerWithDelay(playerId,mailId,tag,delay)
            message = {
                "type": "success",
                "timeStamp": timeStamp
            }

        elif requestType == "reachCondition":
            tag = bodyDic["tag"]
            result = mailSystem.reachConditionIndex(playerId,tag,mailId)
            if result != False:
                message = {
                    "type": "success",
                    "mail": result
                }
            else :
                message = {
                    "type": "fail",
                    "reason": f"out of index of tag {tag}"
                }

        if message:
            print(f"mailSys: message is {message}")
            self.write(message)
            self.flush()
            self.finish()


class MailSystem(object):
    def __init__(self):
        super().__init__()
        self.mailSysConfig = None
        with open("../configs/mailSysConfig.json") as f:
            self.mailSysConfig = json.load(f)[0]
    
    async def sendOneMailToPlayerWithDelay(self, playerId, mailId, tag, delay):
        await asyncio.sleep(delay)
        timeStamp = self.sendOneMailToPlayer(playerId,mailId,tag)
        return timeStamp

    def sendOneMailToPlayer(self, playerId, mailId,tag):
        playerData = dataMgr.dataMgr.getPlayerDataById(playerId)
        mail = {
            "status": 0, #0 = unreaded , 1 = readed,
            "tag": tag,
            "timeStamp": time.time(),
            "selectedOptionIndex": -1
        }
        playerData["mails"][str(mailId)] = mail
        return mail["timeStamp"]

    def reachConditionIndex(self, playerId, tag, mailId):
        playerData = dataMgr.dataMgr.getPlayerDataById(playerId)
        currentTagIndex = playerData["mailConditionIndex"][tag]
        totalLen = len(self.mailSysConfig[tag]["conditions"])
        if currentTagIndex + 1 < totalLen:
            playerData["mailConditionIndex"][tag] += 1
            mail = {
                "status": 0, #0 = unreaded , 1 = readed,
                "tag": tag,
                "timeStamp": time.time(),
                "selectedOptionIndex": -1
            }
            playerData["mails"][str(mailId)] = mail
            return mail
        else:
            return False

    def initMailSysData(self, givenInitDic):
        for key in self.mailSysConfig:
            givenInitDic["mailConditionIndex"][key] = 0
        
    def readOneMail(self,playerId, mailId, index):
        playerData = dataMgr.dataMgr.getPlayerDataById(playerId)
        mail = None
        try:
            mail = playerData["mails"][str(mailId)]
        except:
            return False
        else:
            mail["status"] = 1
            mail["selectedOptionIndex"] = index
            return True

mailSystem = MailSystem()