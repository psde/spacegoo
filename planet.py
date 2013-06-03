import math, time

from backend import *
#from state import *

class Planet:
	def __init__(self, state, data):
		self.state = state
		self.id = int(data['id'])
		self.owner = int(data['owner_id'])
		self.x = int(data['x'])
		self.y = int(data['y'])
		self.ships = data['ships']
		self.production = data['production']

	def distTo(self, other):
		xdiff = self.x - other.x
		ydiff = self.y - other.y
		return int(math.ceil(math.sqrt(xdiff*xdiff + ydiff*ydiff)))

	def getNearestPlanet(self, planets):
		nearest = None
		for planet in planets:
			if nearest == None or self.distTo(nearest) > self.distTo(planet):
				nearest = planet
		return nearest


	def getNearestPlanetDist(self, planets):
		nearest = self.getNearestPlanet(planets)
		if nearest is None:
			return 99999999
		return nearest.distTo(self)

	def istSafeToLeave(self, ships):
		remaining = map(lambda s, l: s-l, self.ships, ships)
		status = self.getStatusIn(500 - self.state.round + 1, remaining)
		return status['owner'] == self.owner

	def getStatusIn(self, eta, starting_ships = None):
		ships_prediction = self.ships[::]
		if starting_ships is not None:
			ships_prediction = starting_ships[::]
		owner_prediction = int(self.owner)

		fleets = self.state.getFleetsTo(self.id)
		for r in range(0, eta + 1):
			# Add production if not neutral
			if owner_prediction != 0:
				ships_prediction = map(lambda s,p: s+p, ships_prediction, self.production)

			# Add incoming fleets
			for fleet in fleets:
				# Is this fleet landing in this round?
				if fleet.eta == r + self.state.round:
					# Reinforcments
					if fleet.owner == owner_prediction:
						ships_prediction = map(lambda s,f: s+f, ships_prediction, fleet.ships)
					# Attacker
					else:
						battle_result = battle(fleet.ships, ships_prediction)
						if sum(battle_result[1]) > 0:
							# Attack unsucsessful
							ships_prediction = battle_result[1]
						else:
							# Attack successful
							ships_prediction = battle_result[0]
							owner_prediction = fleet.owner

		return {'owner': owner_prediction, 'ships': ships_prediction}

	def attackResultsIn(self, ships, rounds):
		status = self.getStatusIn(rounds)
		return battle(self.ships, ships)

	def checkForAttackPossibility(self, other):
		eta = self.distTo(other)
		other_status = other.getStatusIn(eta)
		battle_result = battle(self.ships, other_status['ships'])

		minimum = getMinimumAttackStrength(self.ships, other_status['ships'], 1)
		minimum = map(lambda x: x+10, minimum)

	def attackScoreTo(self, other, calcOtherScore = True):
		if self.owner == other.owner:
			print "Error: Planets have same owner"
			time.sleep(0.5)

		eta = self.distTo(other)
		status =  other.getStatusIn(eta)
		modifier = 0
		if status['owner'] == self.owner:
			if self.state.round <= 255:
				return None
			elif self.owner == 0:
				pass
			else:
				modifier -= 20.0
			#pass

		# Check if we lose this planet
		if self.getStatusIn(eta)['owner'] != self.owner:
			modifier -= 50.0

		if calcOtherScore:
			other_score = other.attackScoreTo(self, False)
			if other_score is not None:
				modifier -= (other_score[0] / 2.5)

		other_ships = status['ships']
		battle_result = battle(self.ships, other_ships)

		if sum(battle_result[0][::]) == 0:
			modifier -= sum(battle_result[1]) / (self.state.round + 0.0001)
			return None
			#pass

		#modifier = 0
		modifier += float(sum(battle_result[0])) / (float(sum(self.ships))+0.0001)
		#modifier += other.planetValue() * 2.5
		modifier -= eta
		#modifier *= float(sum(self.ships[::])) / 10.0
		#modifier += other.planetValue() / 100.0

		# will this break?!
		minimum = getMinimumAttackStrength(self.ships, other_ships, 1)
		minimum = map(lambda x: int(x*1.5), minimum)
		#minimum = self.ships

		#own fleets count against mod
		#for fleet in self.state.getFleetsByTo(other.id, self.state.player_me.id):
		#	modifier -= sum(fleet.ships[::]) / 25.0

		for fleet in self.state.getFleetsByTo(self.id, self.state.player_enemy.id):
			modifier -= sum(fleet.ships) / 8.0

		return [modifier, minimum]

	def shipQuantifier(self):
		q = self.ships[0] + self.ships[1] + self.ships[2]
		return q

	def productionQuantifier(self):
		q = self.production[0] + self.production[1] + self.production[2]
		return q

	def planetValue(self):
		return float(self.productionQuantifier())