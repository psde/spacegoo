class Player:
	def __init__(self, state, data):
		self.state = state
		self.id = data['id']
		self.name = data['name']
		self.isMe = data['itsme']