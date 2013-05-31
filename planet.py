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

	def invasionChances(self, other):
		#a = (self.ships[0] - other.ships[0]) + (self.ships[1] - other.ships[1]) + (self.ships[1] - other.ships[1]) 
		test = battle(self.ships, other.ships)
		#a = (test[0][0] - test[1][0]) + (test[0][1] - test[1][1]) + (test[0][2] - test[1][2])
		a = (test[1][0] - test[0][0]) + (test[1][1] - test[0][1]) + (test[1][2] - test[0][2])
		return a / 3.0

	def score(self, other):
		#return self.invasionChances(other)
		eta = self.distTo(other)
		other_ships = [0, 0, 0]
		for i in range(0, 3):
			other_ships[i] = other.ships[i] + (other.production[i] * eta)

		test = battle(self.ships, other_ships)
		#a = (test[0][0] - test[1][0]) + (test[0][1] - test[1][1]) + (test[0][2] - test[1][2])
		a = (test[1][0] - test[0][0]) + (test[1][1] - test[0][1]) + (test[1][2] - test[0][2])
		return a

	def shipQuantifier(self):
		q = self.ships[0] + self.ships[1] + self.ships[2]
		return q

	def productionQuantifier(self):
		q = self.production[0] + self.production[1] + self.production[2]
		return q