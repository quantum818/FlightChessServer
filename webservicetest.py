import json
import string
import threading
import time
from websocket_server import WebsocketServer
from FlightChess import *

# 通信消息
exitFlag = 0

class table:
	player_list = []
	table_id = 0
	tableplayers={}
	nowPlayer=0
	isGaming=False
	sixTimes=0
	dicP=0
	def __init__(self,id):
		self.table_id = id
		self.player_list = []
		self.tableplayers={}
		self.nowPlayer=0
		self.isGaming=False
		self.sixTimes=0
		self.dicP=0
class Message:
	__Halldata = {"MSGKind": "", "timeNow": "", "sendHost": "","RoomID":0, "MSG": ""}
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
	def setHalldata(self, MSGKind, timeNow, sendHost, MSG, id):
		self.__Halldata["MSGKind"] = MSGKind
		self.__Halldata["timeNow"] = timeNow
		self.__Halldata["sendHost"] = sendHost
		self.__Halldata["MSG"] = MSG
		self.__Halldata["RoomID"] = id
	def sendHalldata(self):
		return json.dumps(self.__Halldata)

# 客户端连接呼叫
def new_client(client, server):
	print("New client connected and was given id %d" % client["id"])
	server.send_message_to_all("new client connect!")
	print(client["address"])
	print('当前连接数'+str(len(server.clients)))
	sendPlayerMSG=Message()
	for player in onlinePlayer:
		sendPlayerMSG.setHalldata("login", "", player, "",0)
		server.send_message(client, sendPlayerMSG.sendHalldata())


# 客户端断开
def client_left(client, server):
	print("Client(%d) disconnected" % client["id"])
	# server.clients.remove(client)
	print('当前连接数'+str(len(server.clients)-1))


# 客户端送信呼叫
def message_received(client, server, message):
	global table1
	global table2
	table1.dicP=0
	table1.sixTimes=0
	table2.dicP=0
	table2.sixTimes=0
	if len(message) > 200:
		message = message[:200] + ".."
	server.send_message_to_all(message)
	getMSG = JSONtoStr(message)
	if message=='table1END':
		table1.player_list.clear()
		table1.tableplayers.clear()
		table1.isGaming=False
		print("table1游戏结束")
	if message=='table2END':
		table2.player_list.clear()
		table2.tableplayers.clear()
		table2.isGaming=False
		print("table2游戏结束")
	if getMSG["MSG"] != "error":
		if getMSG["MSGKind"] == "login":
			onlinePlayer.append(getMSG["sendHost"])
		client["name"]=getMSG["sendHost"]
		print("Client(%d) said: %s"% (client["id"],getMSG["MSGKind"]+ " "+ getMSG["timeNow"]+ " "+ getMSG["sendHost"]+ " "+ getMSG["MSG"],))
		isInList = True
		if getMSG["MSGKind"] == "game":
			if getMSG["MSG"] == "table1":	
				for user in table1.player_list:
					if user == getMSG["sendHost"]:
						isInList = False
						break
				if isInList and getMSG["MSG"] == "table1":
					table1.player_list.append(getMSG["sendHost"])
					table1.tableplayers[getMSG["sendHost"]]=0
					#templist=table1.player_list.copy()
					#reversed(templist)
					for player in table1.player_list:
						data = {"MSGKind": "game", "timeNow": " ", "sendHost": player,"RoomID":1, "MSG": "player"}
						server.send_message(client,StrtoJSON(data))
					print(table1)
				data = {"MSGKind": "game", "timeNow": " ", "sendHost": "admin","RoomID":1, "MSG": "start"}
				if len(table1.player_list) == 4:
					i=1
					msg=Message()
					for user in table1.player_list:
						msg.setHalldata('round','',user,str(i),1)
						temp=msg.sendHalldata()
						server.send_message_to_all(temp)
						i+=1
					server.send_message_to_all(StrtoJSON(data))
					table1.isGaming = True
			elif getMSG["MSG"]=="table2":
				for user in table2.player_list:
					if user == getMSG["sendHost"]:
						isInList = False
						break
				if isInList and getMSG["MSG"] == "table2":
					table2.player_list.append(getMSG["sendHost"])
					table2.tableplayers[getMSG["sendHost"]]=0
					for player in table2.player_list:
						data = {"MSGKind": "game", "timeNow": " ", "sendHost": player,"RoomID":2, "MSG": "player"}
						server.send_message(client,StrtoJSON(data))
					print(table2)
				data = {"MSGKind": "game", "timeNow": " ", "sendHost": "admin","RoomID":2, "MSG": "start"}
				if len(table2.player_list) == 2:
					i=1
					msg=Message()
					for user in table2.player_list:
						msg.setHalldata('round','',user,str(i),0)
						temp=msg.sendHalldata()
						server.send_message_to_all(temp)
						i+=1
					server.send_message_to_all(StrtoJSON(data))
					table2.isGaming = True
				
	else :
		print(message)
	if message[1]=='1':
		if message[0]=='1':
			sendMSG=Message()
			table1.diceP=random.randint(1,6)
			if table1.diceP==6:table1.sixTimes+=1
			sendMSG.setGameCommand('Comm',table1.diceP,True,table1.player_list[0],1)
			table1.nowPlayer=1
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if message[0]=='2':
			sendMSG=Message()
			table1.diceP=random.randint(1,6)
			if table1.diceP==6:table1.sixTimes+=1
			sendMSG.setGameCommand('Comm',table1.diceP,True,table1.player_list[1],1)
			table1.nowPlayer=2
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if message[0]=='3':
			sendMSG=Message()
			table1.diceP=random.randint(1,6)
			if table1.diceP==6:table1.sixTimes+=1
			sendMSG.setGameCommand('Comm',table1.diceP,True,table1.player_list[2],1)
			table1.nowPlayer=3
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if message[0]=='4':
			sendMSG=Message()
			table1.diceP=random.randint(1,6)
			if table1.diceP==6:table1.sixTimes+=1
			sendMSG.setGameCommand('Comm',table1.diceP,True,table1.player_list[3],1)
			table1.nowPlayer=4
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if table1.sixTimes==2:
			table1.diceP=0
			table1.sixTimes=0
		if message[0]=='C': # and diceP!=6:
			if table1.nowPlayer==4:table1.nowPlayer=0
			server.send_message_to_all(table1.player_list[table1.nowPlayer])
		# server.send_message_to_all(message)
	elif message[1]=='2':
		if message[0]=='1':
			sendMSG=Message()
			table2.diceP=random.randint(1,6)
			if table2.diceP==6:table2.sixTimes+=1
			sendMSG.setGameCommand('Comm',table2.diceP,True,table2.player_list[0],2)
			table2.nowPlayer=1
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if message[0]=='2':
			sendMSG=Message()
			table2.diceP=random.randint(1,6)
			if table2.diceP==6:table2.sixTimes+=1
			sendMSG.setGameCommand('Comm',table2.diceP,True,table2.player_list[1],2)
			table2.nowPlayer=2
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if message[0]=='3':
			sendMSG=Message()
			table2.diceP=random.randint(1,6)
			if table2.diceP==6:table2.sixTimes+=1
			sendMSG.setGameCommand('Comm',table2.diceP,True,table2.player_list[2],2)
			table2.nowPlayer=3
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if message[0]=='4':
			sendMSG=Message()
			table2.diceP=random.randint(1,6)
			if table2.diceP==6:table2.sixTimes+=1
			sendMSG.setGameCommand('Comm',table2.diceP,True,table2.player_list[3],2)
			table2.nowPlayer=4
			server.send_message_to_all(sendMSG.sendGamedCommand())
		if table2.sixTimes==2:
			table2.diceP=0
			table2.sixTimes=0
		if message[0]=='C': # and diceP!=6:
			if table2.nowPlayer==2:table2.nowPlayer=0
			server.send_message_to_all(table2.player_list[table2.nowPlayer])

def JSONtoStr(getJSONStr):
	data = {"MSGKind": "", "timeNow": "", "sendHost": "", "RoomID":0,"MSG": ""}
	try:
		if type(json.loads(getJSONStr)) is dict:
			data = json.loads(getJSONStr)
		else:
			data["MSG"]='error'
		if data["MSGKind"]!="game" and data["MSGKind"]!="chat" and data["MSGKind"]!="login":
			data["MSG"]='error'
	except:
		data["MSG"]='error'
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
onlinePlayer=[]
table1=table(1)
table2=table(2)
sendtime=0
Chessboard = FlightChess(table1.player_list)
server = WebsocketServer(host="0.0.0.0", port=PORT)
print('服务端启动|系统时间：'+time.asctime( time.localtime(time.time())))
print('当前连接数'+str(len(server.clients)))
server.set_fn_new_client(new_client)
server.set_fn_client_left(client_left)
server.set_fn_message_received(message_received)
server.run_forever()
