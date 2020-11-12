class Telemetry:
	def __init__(self, GS_IP, GS_PORT, DELAY, SOCKETIO_HOST, SOCKETIO_PORT, on_message):
		self.GS_IP = GS_IP
		self.GS_PORT = GS_PORT
		self.DELAY = DELAY
		self.SOCKETIO_HOST = SOCKETIO_HOST
		self.SOCKETIO_PORT = SOCKETIO_PORT
		self.on_message = on_message

	def reset(self):
		pass

	def warn(self, type, payload):
		print("Warning:", type, payload)

	def log(self, type, payload):
		pass

	@classmethod
	def from_config(cls, config, on_message):
		GS_IP = config['GS_IP']
		GS_PORT = config['GS_PORT']
		DELAY = config['DELAY']
		SOCKETIO_HOST = config['SOCKETIO_HOST']
		SOCKETIO_PORT = config['SOCKETIO_PORT']

		return cls(GS_IP, GS_PORT, DELAY, SOCKETIO_HOST, SOCKETIO_PORT, on_message)
