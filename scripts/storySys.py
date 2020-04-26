from baseHttpHandler import BaseHttpHandler
import dataMgr
import json

class StorySysHandler(BaseHttpHandler):
    def post(self):
        body = self.request.body
        bodyDic = json.loads(body)
        playerId = bodyDic["playerId"]
        requestType = bodyDic["requestType"]
        message = None
        if requestType == "completeCurrent":
            result = storySys.onCompleteCurrentStory(playerId)
            message = {
                "type": "success",
                "storyId": result
            }
        if message:
            self.write(message)
            self.flush()
            self.finish()



class StorySys(object):
    def __init__(self):
        super().__init__()
        self.config = None
        with open("../configs/storySysConfig_server.json") as f:
            self.config = json.load(f)[0]
        

    def onCompleteCurrentStory(self,playerId):
        playerData = dataMgr.dataMgr.getPlayerDataById(playerId)
        index = playerData["storySysIndex"]
        
        if index == len(self.config["storySequence"]) - 1 or index == -1:
            index = -1
            playerData["storySysIndex"] = -1
            playerData["storySysId"] = -1
        else:
            index += 1
            playerData["storySysIndex"] = index
            playerData["storySysId"] = self.config["storySequence"][index]
        
        return playerData["storySysId"]

    def setupInitIndex(self,givenDic):
        if (len(self.config["storySequence"]) == 0):
            givenDic["storySysId"] = -1
            givenDic["storySysIndex"] = -1
        else:
            givenDic["storySysId"] = self.config["storySequence"][0]
            givenDic["storySysIndex"] = 0

storySys = StorySys()