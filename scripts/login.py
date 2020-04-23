import sqlite3
from enums import LoginCodeType,ERRO_CODE,playerAccoutDBName
from baseHttpHandler import BaseHttpHandler
import json
import dbMgr
import register
import time
import tornado.httpclient

appSecret = "f6e3465eca0937e0fd1b9912768e3d15"
appId = "wx5bef670899af8812"

class LoginHandler(BaseHttpHandler):
    async def post(self):
        print(f"LoginHandler: one connection from {self.request.remote_ip}, time: {time.time()}")
        body = self.request.body
        bodyDic = json.loads(body)
        code = bodyDic["code"]
        codeType = bodyDic["codeType"]

        playerId = await getPlayerIdByCode(code,codeType)
        message = None
        if (playerId != None):
            if (playerId != -1):
                message = {"type":"login_success","playerId":playerId}
            else:
                message = {"type":"login_fail","reason":ERRO_CODE.WRONG_PASSWORD.value}
        else:
            message = {"type":"login_fail","reason":ERRO_CODE.NO_SUCH_PLAYER.value}
        
        if (message):
            self.write(message)
            self.flush()
            self.finish()
            print(message)


async def getPlayerIdByCode(code,codeType):
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
        httpClient = tornado.httpclient.AsyncHTTPClient()
        url = f"https://api.weixin.qq.com/sns/jscode2session?appid={appId}&secret={appSecret}&js_code={code}&grant_type=authorization_code"
        
        request = tornado.httpclient.HTTPRequest(url)
        request.validate_cert = False
        response = await httpClient.fetch(request)
        body = str(response.body,encoding="utf-8")
        body = json.loads(body)
        openId = body["openid"]
        print(f"open id is {openId}")
        results = dbMgr.queryMathResultFromTable(openId,"wechatOpenId")
        playerId = None
        if (len(results) > 0):
            playerId = results[0][0]
            
        else:
            playerId = register.registeOnePlayerByCode(openId,LoginCodeType.WECHAT_GAME)
        if (playerId != None):
            return playerId
        else:
            return None

    if (codeType == LoginCodeType.DEVICE_ID.value):
        results = dbMgr.queryMathResultFromTable(code,"deviceId")
        playerId = None
        if (len(results) > 0):
            playerId = results[0][0]
        
        else:
            #regist one player by device id
            playerId = register.registeOnePlayerByCode(code,LoginCodeType.DEVICE_ID)
        
        if (playerId != None):
            return playerId

        else: 
            return None