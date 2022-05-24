import random


class FlightChess(object):
    """玩家类"""
    class Chess:
        host=''
        name=0
        nowRow=0
        localition=0
        state=0
        def __init__(self,ind,num):
            self.host=ind
            name=num

    class PlayerInfo:
        playerName=''
        color=0
        lastChess=4
        WinChess=0
        GetPoint=0
        WinLocal=0
        chess=[]
        def __init__(self,ind,co):
            self.chess=[]
            self.playerName=ind
            self.color=co
            for i in range(4):
                self.chess.append(Chess(ind,i+1))
    players=[]
    def __init__(self,ind):
        self.players=[]
        res=random.sample(range(1,5), 4)
        i=0
        for getplayer in ind:
            self.players.append(PlayerInfo(getplayer,res[i]))
            ++i
    
    


