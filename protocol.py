from abc import ABCMeta, abstractmethod

class Protocol(object):
	__metaclass__ = ABCMeta

	def __init__(self):
		self.src = ""
		self.dst = ""

	def __enter__(self):
		return self

	def __exit__(self):
		pass

	@abstractmethod
	def msgRecv(self):
		pass

	@abstractmethod
	def msgSend(self):
		pass

	@abstractmethod
	def notifyRecv(self):
		pass

	@abstractmethod
	def notifySend(self):
		pass
