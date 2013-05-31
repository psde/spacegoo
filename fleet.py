from backend import *
#from state import *

class Fleet:
	def __init__(self, state, data):
		self.state = state
		self.id = data['id']
		self.owner = data['owner_id']
		self.origin = data['origin']
		self.target = data['target']
		self.eta = data['eta']
		self.ships = data['ships']