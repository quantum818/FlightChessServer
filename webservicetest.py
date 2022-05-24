import json
import string
import threading
from websocket_server import WebsocketServer
from FlightChess import *

# 通信消息
exitFlag = 0


class Message:
	__Halldata = {"MSGKind": "", "timeNow": "", "sendHost": "", "MSG": ""}
	__round = {"Host":"",'tRound': -1}
	__Gamedata = {
		"MSGKind": "",
		"sendhost": "",
		"ChessName": -1,
		"ChessRow": -1,
		"ChessLocal": -1,
		"States": -1,
		"roomID": -1,
	}
	__GamedCommand = {
		"MSGKind": "",
		"DicePoint": -1,
		"DiceState": False,
		"Host": "",
		"roomID": -1,
	}

	def getNormalMSG(self, jsonStr):
		self.Halldata = json.loads(jsonStr)

	def msgKind_hall(self):
		return self.__Halldata["MSGKind"]

	def msgKind_game(self):
		return self.__Gamedata["MSGKind"]

	def timeNow(self):
		return self.__Halldata["timeNow"]

	def sendHost(self):
		return self.__Halldata["sendHost"]

	def MSG(self):
		return self.__Halldata["MSG"]

	def ChessName(self):
		return self.__Gamedata["ChessName"]

	def ChessRow(self):
		return self.__Gamedata["ChessRow"]

	def ChessLocal(self):
		return self.__Gamedata["ChessLocal"]

	def States(self):
		return self.__Gamedata["States"]

	def getHalldata(self, JSONStr):
		self.__Halldata = json.loads(JSONStr)

	def getGamedata(self, JSONStr):
		self.__Gamedata = json.loads(JSONStr)

	def getGamedCommand(self, JSONStr):
		self.__GamedCommand = json.loads(JSONStr)
	
	def sendGamedCommand(self):
		return json.dumps(self.__GamedCommand)

	def setGameCommand(self, MSGKind, DicePoint, DiceState, Host, id):
		self.__GamedCommand["MSGKind"] = MSGKind
		self.__GamedCommand["DicePoint"] = DicePoint
		self.__GamedCommand["DiceState"] = DiceState
		self.__GamedCommand["Host"] = Host
		self.__GamedCommand["roomID"] = id
	
	def setround(self,host,round):
		self.__round['Host']=host
		self.__round['tRound']=round
	
	def sendround(self):
		return json.dumps(self.__round)
	def setHalldata(self, MSGKind, timeNow, sendHost, MSG):
		self.__Halldata["MSGKind"] = MSGKind
		self.__Halldata["timeNow"] = timeNow
		self.__Halldata["sendHost"] = sendHost
		self.__Halldata["MSG"] = MSG
	def sendHalldata(self):
		return json.dumps(self.__Halldata)

# 客户端连接呼叫
def new_client(client, server):
	print("New client connected and was given id %d" % client["id"])
	server.send_message_to_all("new client connect!")


# 客户端断开
def client_left(client, server):
	print("Client(%d) disconnected" % client["id"])


# 客户端送信呼叫
def message_received(client, server, message):
	global isGaming
	global table1
	global nowPlayer
	global table1Player
	diceP=0
	sixTimes=0
	if len(message) > 200:
		message = message[:200] + ".."
	server.send_message_to_all(message)
	if not isGaming:
		getMSG = JSONtoStr(message)
		print("Client(%d) said: %s"% (client["id"],getMSG["MSGKind"]+ " "+ getMSG["timeNow"]+ " "+ getMSG["sendHost"]+ " "+ getMSG["MSG"],))
		isInList = True
		if getMSG["MSGKind"] == "game":
			for user in table1:
				if user == getMSG["sendHost"]:
					isInList = False
					break
			if isInList and getMSG["MSG"] == "table1":
				table1.append(getMSG["sendHost"])
				table1Player[getMSG["sendHost"]]=0
				print(table1)
			data = {"MSGKind": "game", "timeNow": " ", "sendHost": "admin", "MSG": "start"}
			if len(table1) == 2:
				i=1
				msg=Message()
				for user in table1:
					msg.setHalldata('round','',user,str(i))
					temp=msg.sendHalldata()
					server.send_message_to_all(temp)
					i+=1
				server.send_message_to_all(StrtoJSON(data))
				isGaming = True
	else :
		print(message)
		if message=='1':
			sendMSG=Message()
			diceP=random.randint(1,6)
			if diceP==6:sixTimes+=1
			sendMSG.setGameCommand('Comm',diceP,True,table1[0],1)
			nowPlayer=1
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if message=='2':
			sendMSG=Message()
			diceP=random.randint(1,6)
			if diceP==6:sixTimes+=1
			sendMSG.setGameCommand('Comm',diceP,True,table1[1],1)
			nowPlayer=2
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if message=='3':
			sendMSG=Message()
			diceP=random.randint(1,6)
			if diceP==6:sixTimes+=1
			sendMSG.setGameCommand('Comm',diceP,True,table1[2],1)
			nowPlayer=3
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if message=='4':
			sendMSG=Message()
			diceP=random.randint(1,6)
			if diceP==6:sixTimes+=1
			sendMSG.setGameCommand('Comm',diceP,True,table1[3],1)
			nowPlayer=4
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if sixTimes==2:
			diceP=0
			sixTimes=0
		if message=='C': # and diceP!=6:
			if nowPlayer==2:nowPlayer=0
			server.send_message_to_all(table1[nowPlayer])
		# server.send_message_to_all(message)

def JSONtoStr(getJSONStr):
	data = {"MSGKind": "", "timeNow": "", "sendHost": "", "MSG": ""}
	data = json.loads(getJSONStr)
	return data


def StrtoJSON(data):
	JSONstr = json.dumps(data)
	return JSONstr


""" def game_received(client, server, message):
	if len(message) > 200:
		message = message[:200] + ".."
	tempMSG = Message()
	tempMSG.getGamedata(message)
	print(tempMSG)


class gameThread(threading.Thread):
	def __init__(self, threadID, name, players):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.players = players
		
	def run(self):
		print("开始游戏：" + self.name)
		GameRoomStart(self.name,self.players)
		print("退出游戏：" + self.name)


def GameRoomStart(threadName, players):
	if exitFlag:
		threadName.exit()
	players = FlightChess(players)
	server.set_fn_message_received(game_received)
	server.run_forever() """


PORT = 9001
table1 = []
table1Player={}
isGaming = False
sendtime=0
nowPlayer=0
Chessboard = FlightChess(table1)
server = WebsocketServer(host="0.0.0.0", port=PORT)
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
