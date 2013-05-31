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
			time.sleep(0.3)
			#return

	def start(self):
		self.state = State()
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.ip, self.port))
		self.io = self.socket.makefile("rw")

		self.write("login %s %s" % (self.credentials.username, self.credentials.password), False)
		print "Logging in"

		self.mainloop()

	# IO
	def write(self, data, printout = True):
		line = '%s\n' % (data,)
		if printout:
			print "<= %s" % (line),
		self.io.write(line)
		self.io.flush()

	def read(self, printout = True):
		data = self.io.readline().strip()
		self.io.flush()
		if data and data[0] != "{" and printout:
			print "=> %s" % (data)
		return data

	def processState(self, state):
		#print "Processing state ..."

		player_id = int(state["player_id"])
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

		my_planet_ships = [0, 0, 0]
		for planet in self.state.getPlanetsByOwner(player_id):
			for i in range(0,3):
				my_planet_ships[i] += planet.ships[i]

		my_fleet_ships = [0, 0, 0]
		for fleet in self.state.getFleetsBy(player_id):
			for i in range(0,3):
				my_fleet_ships[i] += fleet.ships[i]

		enemy_planet_ships = [0, 0, 0]
		for planet in self.state.getPlanetsByOwner(enemy_id):
			for i in range(0,3):
				enemy_planet_ships[i] += planet.ships[i]

		enemy_fleet_ships = [0, 0, 0]
		for fleet in self.state.getFleetsBy(enemy_id):
			for i in range(0,3):
				enemy_fleet_ships[i] += fleet.ships[i]

		decision = self.state.getDecision()

		self.write(decision.command, False)

		print "^=============^"
		print "Round %s, Enemy: %s" %(self.state.round, self.state.getPlayerById(enemy_id).name)
		print "---------------"
		print "M: PC %s\tPS %s\tFS %s" % (len(self.state.getPlanetsByOwner(player_id)), my_planet_ships, my_fleet_ships)
		print "E: PC %s\tPS %s\tFS %s" % (len(self.state.getPlanetsByOwner(enemy_id)), enemy_planet_ships, enemy_fleet_ships)
		print "Decision '%s' with score %s ('%s')" % (decision.description, decision.score, decision.command)
		print "v=============v"
		#time.sleep(0.1)

		return False

	def mainloop(self):
		while True:
			line = self.read(False)
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