import sqlite3
from enums import LoginCodeType,ERRO_CODE,playerAccoutDBName
from baseHttpHandler import BaseHttpHandler
import json
import dbMgr
import register
import time

class LoginHandler(BaseHttpHandler):
    def post(self):
        print(f"one connection from {self.request.remote_ip}, time: {time.time()}")
        body = self.request.body
        bodyDic = json.loads(body)
        code = bodyDic["code"]
        codeType = bodyDic["codeType"]

        playerId = getPlayerIdByCode(code,codeType)
        message = None
        if (playerId != None):
            if (playerId != -1):
                message = {"type":"login_success","playerId":playerId}
            else:
                message = {"type":"login_fail","reason":ERRO_CODE.WRONG_PASSWORD.value}
        else:
            message = {"type":"login_fail","reason":ERRO_CODE.NO_SUCH_PLAYER.value}
        
        if (message):
            print(f"message is {message}")
            self.write(message)
            self.flush()
            self.finish()



def getPlayerIdByCode(code,codeType):
    if (codeType == LoginCodeType.ACCOUT_AND_PASSWORD.value):
        temp = code.split("&&&")
        account = temp[0]
        password = temp[1]
        accountDB = sqlite3.connect(playerAccoutDBName)
        cursor = accountDB.cursor()
        cursor.execute("select * from user where accout = ?" , (account,))
        values = cursor.fetchall()

        if (len(values) >= 1):
            oneValue = values[0]
            playerId = oneValue[0]
            password_db = oneValue[2]
            if (password_db == password):
                cursor.close()
                accountDB.close()
                return playerId
            else:
                return -1
        else:
            return None

    if (codeType == LoginCodeType.WECHAT_GAME.value):
        results = dbMgr.queryMathResultFromUserTable(code,"wechatOpenId")
        playerId = None
        if (len(results) > 0):
            playerId = results[0][0]
            
        else:
            playerId = register.registeOnePlayerByCode(code,LoginCodeType.WECHAT_GAME)
        if (playerId != None):
            return playerId
        else:
            return None

    if (codeType == LoginCodeType.DEVICE_ID.value):
        results = dbMgr.queryMathResultFromUserTable(code,"deviceId")
        playerAccoutDBName = None
        if (len(results) > 0):
            playerId = results[0][0]
        
        else:
            #regist one player by device id
            playerId = register.registeOnePlayerByCode(code,LoginCodeType.DEVICE_ID)
        
        if (playerId != None):
            return playerId

        else: 
            return None