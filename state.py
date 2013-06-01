import time, math

from planet import *
from fleet import *
from player import *

class Decision:
	def __init__(self, score, origin, description, command = "nop"):
		self.score = score
		self.origin = origin
		self.description = description
		self.command = command

	def __repr__(self):
		return "<%s, %s, '%s'>" % (self.score, self.command, self.description)

class State:
	def __init__(self):
		self._PRIORITY_RALLY = -99999999.0
		self._PRIORITY_GRIEF = -1.0
		self._PRIORITY_FLEE = 1.5
		self._PRIORITY_COLONIZE = 4.0
		self._PRIORITY_ATTACK = 5.5
		self._PRIORITY_DEFEND = -999.0

		self.round = 0
		self.stack = []
		self.planets = []
		self.fleets = []

	def update(self, data):
		#self.stack.append([self.planets, self.fleets])
		self.planets = [Planet(self, planet) for planet in data['planets']]
		self.fleets = [Fleet(self, fleet) for fleet in data['fleets']]
		self.players = [Player(self, player) for player in data['players']]
		self.round = int(data['round'])

		for player in self.players:
			if player.isMe:
				self.player_me = player
			else:
				self.player_enemy = player
 
		# Copy const attributes
		self.PRIORITY_RALLY = self._PRIORITY_RALLY
		self.PRIORITY_FLEE = self._PRIORITY_FLEE
		self.PRIORITY_GRIEF = self._PRIORITY_GRIEF
		self.PRIORITY_COLONIZE = self._PRIORITY_COLONIZE
		self.PRIORITY_ATTACK = self._PRIORITY_ATTACK
		self.PRIORITY_DEFEND = self._PRIORITY_DEFEND

		# Bot specific
		#if self.player_enemy.name == "conquerbot":
		#	self.PRIORITY_ATTACK /= 2
		#	self.PRIORITY_DEFEND *= 4
		#	#self.PRIORITY_RALLY = 5
		#	self.PRIORITY_COLONIZE /= 3


		#if self.player_enemy.name == "chrtio":
		#	self.PRIORITY_ATTACK /= 8
		#	self.PRIORITY_COLONIZE /= 3.5

		#if self.player_enemy.name == "nomeataintercept2":
		#	self.PRIORITY_ATTACK *= 3
		#	self.PRIORITY_DEFEND /= 4
		#	self.PRIORITY_COLONIZE /= 2

		if self.round >= 320:
			self.PRIORITY_RALLY = self.PRIORITY_ATTACK - 0.1
		if self.round >= 390:
			self.PRIORITY_ATTACK *= 20

	def getPlayerById(self, id):
		r = [player for player in self.players if player.id == id]
		return r[0]

	def getPlanetsByOwner(self, id):
		return [planet for planet in self.planets if planet.owner == id]

	def getFleetsTo(self, target):
		return [fleet for fleet in self.fleets if fleet.target == target]

	def getFleetsBy(self, id):
		return [fleet for fleet in self.fleets if fleet.owner == id]

	def getFleetsByTo(self, id, target):
		return [fleet for fleet in self.fleets if fleet.owner == id and fleet.target == target]

	def getDecision(self):
		decisions = [Decision(-9999.9, None, 'Default decision')]

		my_planets = self.getPlanetsByOwner(self.player_me.id)
		enemy_planets = self.getPlanetsByOwner(self.player_enemy.id)

		# Griefing decisions
		for origin in my_planets:
			if sum(origin.ships[::]) < 3:
				continue
			for target in enemy_planets:
				if sum(origin.ships[::]) < 3:
					continue

				s = [min(origin.ships[0], target.production[0], 1), min(origin.ships[1], target.production[1], 1), min(origin.ships[2], target.production[2], 1)]
				modifier = sum(s[::]) / origin.distTo(target)
				c = "send %s %s %s %s %s" % (origin.id, target.id, s[0], s[1], s[2])
				d = Decision((self.PRIORITY_GRIEF + modifier), origin, "Griefing planet", c)
				#decisions.append(d)

		# Rally decisions
		for origin_planet in my_planets:
			for target_planet in my_planets:
				# Skip same ones
				if origin_planet.id == target_planet.id:
					continue

				min_dist = 999999
				for enemy_planet in enemy_planets:
					if enemy_planet.distTo(target) < min_dist:
						min_dist = enemy_planet.distTo(target)

				#modifier = (target_planet.planetValue() / origin_planet.planetValue()) / 100.0
				#modifier = sum(origin_planet.ships[::]) / (100.0 * (self.round+0.0001))
				modifier = (min_dist / 10.0) * sum(origin_planet.ships[::])

				c = "send %s %s %s %s %s" % (origin_planet.id, target_planet.id, origin_planet.ships[0]/2, origin_planet.ships[1]/2, origin_planet.ships[2]/2)
				d = Decision((self.PRIORITY_RALLY + modifier), origin_planet, "Rally ships", c)
				decisions.append(d)

		# Fleeing decisions
		if len(my_planets) > 1:
			for origin_planet in my_planets:
				for fleet in self.getFleetsByTo(self.player_enemy.id, origin_planet.id):
					if fleet.eta == self.round + 1:
						battle_result = battle(origin_planet.ships, fleet.ships)
						if sum(battle_result[0][::]) == -1:
							best = None
							dist = 99999999
							for target in my_planets:
								if target.id == origin_planet.id:
									continue
								if best == None or origin_planet.distTo(target) < dist:
									best = target
									dist = origin_planet.distTo(target)
							modifier = sum(origin_planet.ships[::]) / 100.0 * self.round
							c = "send %s %s %s %s %s" % (origin_planet.id, best.id, origin_planet.ships[0], origin_planet.ships[1], origin_planet.ships[2])
							d = Decision((self.PRIORITY_FLEE + modifier), origin_planet, "Fleeing from enemy", c)
							decisions.append(d)

		# Defend decisions
		for planet in my_planets:
			for fleet in self.getFleetsByTo(self.player_enemy.id, planet.id):
				rounds_left = int(fleet.eta - self.round)
				if rounds_left == 1:
					continue

				status = planet.getStatusIn(rounds_left)
				if status['owner'] != self.player_me.id:
					# Needs help!
					for helper in my_planets:
						if planet.distTo(helper) < rounds_left and planet != helper:
							# is near enough to help
							helper_status = helper.getStatusIn(int(rounds_left*0.5))
							if helper_status['owner'] == self.player_me.id:
								# can help
								modifier = sum(fleet.ships[::]) / 10.0
								c = "send %s %s %s %s %s" % (helper.id, planet.id, status['ships'][0], status['ships'][1], status['ships'][2])
								d = Decision((self.PRIORITY_DEFEND + modifier), helper, "Reinforcing planet", c)
								decisions.append(d)


		# Colonize decisions
		for neut_planet in self.getPlanetsByOwner(0):
			for my_planet in my_planets:
				foo = my_planet.attackScoreTo(neut_planet)
				if foo is None:
					continue

				c = "send %s %s %s %s %s" % (my_planet.id, neut_planet.id, foo[1][0], foo[1][1], foo[1][2])
				d = Decision((self.PRIORITY_COLONIZE + foo[0] + neut_planet.planetValue() * 2.3), my_planet, "Colonizing neutral planet", c)
				decisions.append(d)

		# Attack decisions
		for enemy_planet in self.getPlanetsByOwner(self.player_enemy.id):
			for my_planet in my_planets:
				foo = my_planet.attackScoreTo(enemy_planet)
				if foo is None:
					continue

				c = "send %s %s %s %s %s" % (my_planet.id, enemy_planet.id, foo[1][0], foo[1][1], foo[1][2])
				d = Decision((self.PRIORITY_ATTACK + foo[0]), my_planet, "Attacking planet", c)
				decisions.append(d)

		decisions.sort(key=lambda x: x.score, reverse=True)

		if decisions[0].command == 'FOFOFOFOFOFOFOFOFOFOFOFOnop':
			best_origin = None
			best_target = None
			best_dist = 9999999999
			for enemy_planet in self.getPlanetsByOwner(self.player_enemy.id):
				if sum(enemy_planet.ships[::]) > 3:
				#if enemy_planet.ships[0] > 1 and enemy_planet.ships[1] > 1 and enemy_planet.ships[2] > 1:
					for my_planet in my_planets:
						if sum(my_planet.ships[::]) > 3:
						#if my_planet.ships[0] > 1 and my_planet.ships[1] > 1 and my_planet.ships[2] > 1:
							dist = my_planet.distTo(enemy_planet)

							if best_origin is None or dist < best_dist:
								best_origin = my_planet
								best_target = enemy_planet
								best_dist = dist

			if best_origin != None:
				c = "send %s %s 1 1 1" % (best_origin.id, best_target.id)
				a = Decision(1337, best_origin, "Griefing planet", c)
				return a

		# Check if a planet needs to def
		def_planet_ids = []
		for my_planet in my_planets:
			ships = [0, 0, 0]
			max_eta = 0
			for fleet in self.fleets:
				if fleet.owner == self.player_enemy.id:
					ships = map(lambda s,f: s+f, ships, fleet.ships)
					if fleet.eta > max_eta:
						max_eta = fleet.eta
			status = my_planet.getStatusIn(max_eta - self.round)
			if status['owner'] != self.player_me.id:
				def_planet_ids.append(my_planet.id)

		decision = decisions[0]
		for i in range(0, len(decisions)):
			if decisions[i].origin in def_planet_ids:
				print "skipping"
				time.sleep(0.5)
				decision = decisions[i]
				break

		return [decision, len(decisions)]