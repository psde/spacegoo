class Player:
	def __init__(self, state, data):
		self.state = state
		self.id = int(data['id'])
		self.name = data['name']
		self.isMe = data['itsme']