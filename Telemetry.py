import json
import socket
from threading import Thread
import time
from Task import Task

from enums import LogPriority

class Telemetry:
	def __init__(self, GS_IP, GS_PORT, DELAY, SOCKETIO_HOST, SOCKETIO_PORT, add_task):
		self.GS_IP = GS_IP
		self.GS_PORT = GS_PORT
		self.DELAY = DELAY
		self.SOCKETIO_HOST = SOCKETIO_HOST
		self.SOCKETIO_PORT = SOCKETIO_PORT
		self.add_task = add_task
		self.CHUNK_SIZE = 4096

		# This is where you specify what gets logged
		self.log_level = LogPriority.WARN

		self.socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.listener = Thread(target=self.listen, daemon=True)

		try:
			self.connect()
			self.listener.start()
		except TimeoutError:
			print("Failed to connect to ground station: Timeout")

	def connect(self):
		self.socket.connect((self.GS_IP, self.GS_PORT))

	def listen(self):
		while True:
			data = self.socket.recv(self.CHUNK_SIZE)
			if not data:
				task = json.loads(data)
				self.add_task(Task(task['action'], task['payload']))
			else:
				# Must have disconnected
				print("Disconnected! Attempting to reconnect...")
				try:
					self.connect()
				except TimeoutError:
					print("Failed to connect to ground station: Timeout")

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
