import json, socket, time

# credentials
import credentials
from planet import *
from fleet import *
from state import *

class Spacegoo:

	def __init__(self, ip, port):
		self.credentials = credentials.Credentials()
		self.ip = ip
		self.port = port

		while True:
			self.start()
			#return

	def start(self):
		self.state = State()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.ip, self.port))
		self.io = self.socket.makefile("rw")

		self.write("login %s %s" % (self.credentials.username, self.credentials.password), "login")

		self.mainloop()

	# IO
	def write(self, data, foo=""):
		line = '%s\n' % (data,)
		print "<= %s" % (line),
		self.io.write(line)
		self.io.flush()

	def read(self):
		data = self.io.readline().strip()
		self.io.flush()
		if data and data[0] != "{":
			print "=> %s" % (data)
		return data

	def processState(self, state):
		print "Processing state ..."

		player_id = state["player_id"]
		enemy_id = 2
		if player_id == 2:
			enemy_id = 1

		if state["game_over"] == True:
			if not state["winner"]:
				print "Draw!"
			elif state["winner"] != player_id:
				print "Loser."
			else:
				print "Winner."
			return True

		self.state.update(state)

		

		self.write("nop")
		return False

		#enemy_planets = [Planet(planet) for planet in state['planets'] if planet['owner_id'] != player_id and planet['owner_id'] != 0]
		#own_planets = [Planet(planet) for planet in state['planets'] if planet['owner_id'] == player_id]
		#neutral_planets = [Planet(planet) for planet in state['planets'] if planet['owner_id'] == 0]

		#print enemy_planets
		#print own_planets
		#print neutral_planets
		#for(p in sorted(neutral_planets, key=lambda x: x., reverse=True))

		if len(neutral_planets) > 0:
			choice = [None, None]
			for o in own_planets:
				for n in neutral_planets:
					inv = n.score(o)

					if choice[0] == None or choice[1].score(choice[0]) < inv:
						if inv > 20.0:
							choice = [o, n]

			if choice[0] != None:
				print "Sending to neut"
				self.write("send %s %s %s %s %s" % (choice[0].id, choice[1].id, choice[0].ships[0], choice[0].ships[1], choice[0].ships[2]))
				return False


		if len(enemy_planets) > 0:
			choice = [None, None]
			for o in own_planets:
				for n in enemy_planets:
					inv = n.score(o)

					if choice[0] == None or choice[1].score(choice[0]) < inv:
						if inv > 30.0:
							choice = [o, n]

			if choice[0] != None:
				print "sending to enemy"
				self.write("send %s %s %s %s %s" % (choice[0].id, choice[1].id, choice[0].ships[0], choice[0].ships[1], choice[0].ships[2]))
				return False

		self.write("nop")
		return False

	def mainloop(self):
		while True:
			line = self.read()
			if line and line[0] == "{":
				data = json.loads(line)
				gameover = self.processState(data)
				#time.sleep(0.05)
				#if gameover:
					#return
			if len(line) == 0:
				return
			if line.startswith("closing"):
				return
			if line.startswith("This game is"):
				return


#s = Spacegoo("spacegoo.gpn.entropia.de", 6000)
s = Spacegoo("94.45.226.23", 6000)