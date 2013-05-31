from planet import *
from fleet import *

class Decision:
	def __init__(self, score, command):
		self.score = score
		self.command = command

class State:
	def __init__(self):
		self.PRIORITY_DEFEND = 1
		self.PRIORITY_COLONIZE = 2
		self.PRIORITY_ATTACK = 3

		self.stack = []
		self.planets = []
		self.fleets = []

	def update(self, data):
		self.stack.append([self.planets, self.fleets])
		self.planets = [Planet(self, planet) for planet in data['planets']]
		self.fleets = [Fleet(self, fleet) for fleet in data['fleets']]

	def getPlanetsByOwner(self, id):
		r = []
		for planet in self.planets:
			if planet.owner == id:
				r.append(planet)
		return r

	def getFleetsTo(self, target, id):
		r = []
		for fleet in self.fleets:
			if fleet.target == target and fleet.owner == id:
				r.append(fleet)
		return r
