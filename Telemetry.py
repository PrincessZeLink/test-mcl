import json

from enums import LogPriority

class Telemetry:
	def __init__(self, GS_IP, GS_PORT, DELAY, SOCKETIO_HOST, SOCKETIO_PORT, on_message):
		self.GS_IP = GS_IP
		self.GS_PORT = GS_PORT
		self.DELAY = DELAY
		self.SOCKETIO_HOST = SOCKETIO_HOST
		self.SOCKETIO_PORT = SOCKETIO_PORT
		self.on_message = on_message

		# This is where you specify what gets logged
		self.log_level = LogPriority.WARN

	def reset(self):
		pass

	def critical(self, type, payload):
		self.log(type, payload. LogPriority.CRITICAL)

	def warn(self, type, payload):
		self.log(type, payload, LogPriority.WARN)

	def info(self, type, payload):
		self.log(type, payload, LogPriority.INFO)

	def log(self, type, payload, priority):
		if priority >= self.log_level:
			packet = {
				"type": type,
				"payload": payload
			}
			print("Info:", json.dumps(packet))


	@classmethod
	def from_config(cls, config, on_message):
		GS_IP = config['GS_IP']
		GS_PORT = config['GS_PORT']
		DELAY = config['DELAY']
		SOCKETIO_HOST = config['SOCKETIO_HOST']
		SOCKETIO_PORT = config['SOCKETIO_PORT']

		return cls(GS_IP, GS_PORT, DELAY, SOCKETIO_HOST, SOCKETIO_PORT, on_message)
