import time
import datetime
import dataMgr

class RefreshSystem(object):
    def __init__(self):
        super().__init__()
        self.refreshTimeHour = 5
        self.refreshTimeMinute = 0
        self.refreshTimeSecond = 0
        # self.playerId = 0
        # self.lastInteractTime = 0
        # self.refreshDelta = None
    
    def onRefresh(self,playerId):
        pass

    def resolveRefresh(self,playerId):
        playerData = dataMgr.dataMgr.getPlayerDataById(playerId)
        lastInteractTime = playerData["lastInteractTime"]
        currentTime = time.time()
        refreshed = False
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
                self.onRefresh(playerId)
                refreshed = True

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
        return (refreshDelta, refreshed)

    
class RefreshSystemMgr(object):
    def __init__(self):
        super().__init__()
        self.systems = []

    
refreshSystemMgr = RefreshSystemMgr()