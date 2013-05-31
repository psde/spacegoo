import math

from backend import *
#from state import *

class Planet:
	def __init__(self, state, data):
		self.state = state
		self.id = data['id']
		self.owner = data['owner_id']
		self.x = data['x']
		self.y = data['y']
		self.ships = data['ships']
		self.production = data['production']

	def distTo(self, other):
		xdiff = self.x - other.x
		ydiff = self.y - other.y
		return int(math.ceil(math.sqrt(xdiff*xdiff + ydiff*ydiff)))

	def getStatusIn(self, eta):
		ships_prediction = self.ships
		owner_prediction = self.owner

		fleets = self.state.getFleetsTo(self.id)
		for r in range(0, eta):
			# Add production
			for i in range(0, 3):
				ships_prediction[i] = ships_prediction[i] + self.production[i]

			# Add incoming fleets
			for fleet in fleets:
				# Is this fleet landing in this round?
				if fleet.eta == r + self.state.round:
					# Reinforcments
					if fleet.owner == self.id:
						for i in range(0, 3):
							ships_prediction[i] = ships_prediction[i] + fleet.ships[i]
					# Attacker
					else:
						battle_result = battle(fleet.ships, ships_prediction)
						if sum(battle_result[0][::]) != 0:
							# Attack successful
							ships_prediction = battle_result[0]
							owner_prediction = fleet.owner
						else:
							# Attack unsucsessful
							ships_prediction = battle_result[1]
		return [owner_prediction, ships_prediction]

	def attackResultsIn(self, ships, rounds):
		status = self.getStatusIn(rounds)
		return battle(self.ships, ships)

	def attackScoreTo(self, other):
		eta = self.distTo(other)
		status =  other.getStatusIn(eta)
		modifier = 0
		if status[0] == self.state.player_me.id:
			return None
			#pass

		other_ships = status[1]
		battle_result = battle(self.ships, other_ships)

		#if sum(battle_result[0][::]) == 0:
		#	modifier -= sum(battle_result[1][::]) / self.state.round
			#return None
			#pass

		#modifier = 0
		#modifier = float(sum(battle_result[0][::])) / (float(sum(self.ships[::]))+0.0001)
		#modifier += other.planetValue()
		modifier -= eta / 10.0
		#modifier += float(sum(battle_result[0][::])) / (float(sum(self.ships[::]))+0.0001)
		#modifier *= float(sum(self.ships[::])) / 10.0
		#modifier -= eta / 10.0
		#modifier += other.planetValue() / 100.0
		minimum = getMinimumAttackStrength(self.ships, other_ships, 1.5)

		#own fleets count against mod
		#for fleet in self.state.getFleetsByTo(other.id, self.state.player_me.id):
		#	modifier -= sum(fleet.ships[::]) / 10.0

		return [modifier, minimum]

	def shipQuantifier(self):
		q = self.ships[0] + self.ships[1] + self.ships[2]
		return q

	def productionQuantifier(self):
		q = self.production[0] + self.production[1] + self.production[2]
		return q

	def planetValue(self):
		return float(self.productionQuantifier())