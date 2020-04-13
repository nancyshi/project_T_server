import baseHttpHandler
import json


class HelperHandler(baseHttpHandler.BaseHttpHandler):
    def post(self):
        body = self.request.body
        bodyDic = json.loads(body)
        dataDic = bodyDic["data"]
        fileStr = json.dumps(dataDic,indent=4)
        with open("../temp/levelSceneConfig.js","w") as f:
            f.write(fileStr)
            print("write success")
        
        self.finish()