from baseHttpHandler import BaseHttpHandler
import json

class LongConnectHandler(BaseHttpHandler):
    def post(self):
        body = self.request.body
        bodyDic = json.loads(body)
        playerId = bodyDic["playerId"]
        requestType = bodyDic["requestType"]
        message = None
        if (requestType == "heartBeat"):
            messages = longConnectMessages.getMessagesByPlayerId(playerId)
            if len(messages) == 0 :
                message = {
                    "type": "heartBeat",
                }
            else:
                message = {
                    "type": "message",
                    "messages": messages
                }
        if message != None:
            self.write(message)
            self.flush()
            self.finish()
            longConnectMessages.initMessagesByPlayerId(playerId)


class LongConnectMessages(object):
    def __init__(self):
        super().__init__()
        self.messages = {}

    def initMessagesByPlayerId(self,playerId):
        self.messages[str(playerId)] = []

    def pushOneMessageByPlayerId(self,playerId,message):
        playerMessages = self.getMessagesByPlayerId(playerId)
        playerMessages.append(message)

    def getMessagesByPlayerId(self,playerId):
        if str(playerId) in self.messages.keys():
            return self.messages[str(playerId)]
        else:
            self.initMessagesByPlayerId(playerId)
            return self.getMessagesByPlayerId(playerId)



longConnectMessages = LongConnectMessages()