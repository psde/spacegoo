import thread, mutex

class Foo:
	def __init__(self, m, id):
		self.mutex = m
		self.id = id

	def tryStart(self):
		while True:
			self.mutex.lock(Foo.start, self)

	def start(self):
		self.mainloop()

	def mainloop(self):

		for i in range(0, 10):
			print "%s> %s" %(self.id, i)

m = mutex.mutex()
for i in range(0, 10):
	f = Foo(m, i)
	thread.start_new_thread(Foo.tryStart, (f,))

while True:
	pass