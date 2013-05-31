from backend import *
#from state import *

class Fleet:
	def __init__(self, state, data):
		self.state = state
		self.id = int(data['id'])
		self.owner = int(data['owner_id'])
		self.origin = int(data['origin'])
		self.target = int(data['target'])
		self.eta = int(data['eta'])
		self.ships = data['ships']