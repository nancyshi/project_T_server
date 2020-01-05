from enum import Enum
class LoginCodeType(Enum):
    WECHAT_GAME = 1
    ACCOUT_AND_PASSWORD = 2
    DEVICE_ID = 3

class ERRO_CODE(Enum):

    NO_SUCH_PLAYER = 1
    WRONG_PASSWORD = 2

playerAccoutDBName = "playerAccout.db"
playerDataDBName = "playerData.db"