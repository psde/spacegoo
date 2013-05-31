import time, math

from planet import *
from fleet import *
from player import *

class Decision:
	def __init__(self, score, description, command = "nop"):
		self.score = score
		self.description = description
		self.command = command

	def __repr__(self):
		return "<%s, %s, '%s'>" % (self.score, self.command, self.description)

class State:
	def __init__(self):
		self.PRIORITY_RALLY = -99999999.0
		self.PRIORITY_FLEE = 1.5
		self.PRIORITY_COLONIZE = 3.0
		self.PRIORITY_ATTACK = 5.0
		self.PRIORITY_DEFEND = 7.0

		self.round = 0
		self.stack = []
		self.planets = []
		self.fleets = []

	def update(self, data):
		self.round = self.round + 1
		#self.stack.append([self.planets, self.fleets])
		self.planets = [Planet(self, planet) for planet in data['planets']]
		self.fleets = [Fleet(self, fleet) for fleet in data['fleets']]
		self.players = [Player(self, player) for player in data['players']]

		for player in self.players:
			if player.isMe:
				self.player_me = player
			else:
				self.player_enemy = player

	def getPlayerById(self, id):
		r = [player for player in self.players if player.id == id]
		return r[0]

	def getPlanetsByOwner(self, id):
		return [planet for planet in self.planets if planet.owner == id]
		r = []
		for planet in self.planets:
			if planet.owner == id:
				r.append(planet)
		return r

	def getFleetsTo(self, target):
		return [fleet for fleet in self.fleets if fleet.target == target]
		r = []
		for fleet in self.fleets:
			if fleet.target == target:
				r.append(fleet)
		return r

	def getFleetsBy(self, id):
		return [fleet for fleet in self.fleets if fleet.owner == id]
		r = []
		for fleet in self.fleets:
			if fleet.owner == id:
				r.append(fleet)
		return r

	def getFleetsByTo(self, id, target):
		return [fleet for fleet in self.fleets if fleet.owner == id and fleet.target == target]
		r = []
		for fleet in self.fleets:
			if fleet.target == target and fleet.owner == id:
				r.append(fleet)
		return r

	def getDecision(self):
		decisions = [Decision(-9999.9, 'Default decision')]

		#if player_enemy.name == "conquerbot":
		#	self.PRIORITY_ATTACK /= 2

		my_planets = self.getPlanetsByOwner(self.player_me.id)

		# Rally decisions
		for origin_planet in my_planets:
			for target_planet in my_planets:
				# Skip same ones
				if origin_planet.id == target_planet.id:
					continue

				modifier = (target_planet.planetValue() / origin_planet.planetValue()) / 100.0
				modifier += sum(origin_planet.ships[::]) / (100.0 * self.round)
				c = "send %s %s %s %s %s" % (origin_planet.id, target_planet.id, origin_planet.ships[0]/2, origin_planet.ships[1]/2, origin_planet.ships[2]/2)
				d = Decision((self.PRIORITY_RALLY + modifier), "Rally ships", c)
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
							d = Decision((self.PRIORITY_FLEE + modifier), "Fleeing from enemy", c)
							decisions.append(d)



		# Defend decisions
		for planet in my_planets:
			for fleet in self.getFleetsByTo(self.player_enemy.id, planet.id):
				rounds_left = int(fleet.eta - self.round)
				if rounds_left == 1:
					continue

				status = planet.getStatusIn(rounds_left)
				if status[0] != self.player_me.id:
					# Needs help!
					for helper in my_planets:
						if planet.distTo(helper) < rounds_left and planet != helper:
							# is near enough to help
							helper_status = helper.getStatusIn(int(rounds_left*1.5))
							if helper_status[0] == self.player_me.id:
								# can help
								modifier = sum(fleet.ships[::]) / 10.0
								c = "send %s %s %s %s %s" % (helper.id, planet.id, status[1][0], status[1][1], status[1][2])
								d = Decision((self.PRIORITY_DEFEND + modifier), "Reinforcing planet", c)
								decisions.append(d)


		# Colonize decisions
		for neut_planet in self.getPlanetsByOwner(0):
			for my_planet in my_planets:
				foo = my_planet.attackScoreTo(neut_planet)
				if foo is None:
					continue

				c = "send %s %s %s %s %s" % (my_planet.id, neut_planet.id, foo[1][0], foo[1][1], foo[1][2])
				d = Decision((self.PRIORITY_COLONIZE + foo[0]), "Colonizing neutral planet", c)
				decisions.append(d)

		# Attack decisions
		for enemy_planet in self.getPlanetsByOwner(self.player_enemy.id):
			for my_planet in my_planets:
				foo = my_planet.attackScoreTo(enemy_planet)
				if foo is None:
					continue

				c = "send %s %s %s %s %s" % (my_planet.id, enemy_planet.id, foo[1][0], foo[1][1], foo[1][2])
				d = Decision((self.PRIORITY_ATTACK + foo[0]), "Attacking planet", c)
				decisions.append(d)

		decisions.sort(key=lambda x: x.score, reverse=True)

		if decisions[0].command == 'nop':
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
				a = Decision(1337, "Griefing planet", c)
				return a


		#print decisions
		return decisions[0]