import time
import serial

class Microcontroller:
	def __init__(self, name: str, address: str, baud: int):
		pass

	def reset(self):
		pass

	def read(self, num_bytes) -> bytes:
		pass

	def write(self, num_bytes) -> bytes:
		pass

	def ping(self, timeout) -> bool:
		pass

import os
class SimulatedArduino(Microcontroller):

	def read(self, num_bytes) -> bytes:
		return os.urandom(num_bytes)

class Arduino(Microcontroller):
	def __init__(self, name: str, address: str, baud: int):
		self.name = name
		self.serial = serial.Serial(address, baud)

	def reset(self):
		self.serial.setDTR(True)
		time.sleep(1)
		self.serial.flush()
		self.serial.reset_input_buffer()
		self.serial.reset_output_buffer()
		self.serial.setDTR(False)
		
		# Wait for arduino to reset
		time.sleep(3)

	def read(self, num_bytes) -> bytes:
		# Blocks until enough bytes are read.
		# To change this, add a timeout to self.serial.read().
		return self.serial.read(num_bytes)

	def write(self, bytes: bytes) -> int:
		# Returns the number of bytes actually written.
		return self.serial.write(bytes)

	def ping(self, timeout) -> bool:
		initial_timeout = self.serial.timeout
		self.serial.timeout = timeout
		self.serial.write(bytes([1]))
		reading = self.serial.read(1)
		self.serial.timeout = initial_timeout
		return len(reading) > 0

READ = 0
SET_PIN = 1

class SensorController:
	def __init__(self, arduino: Microcontroller):
		self.arduino = arduino

	def read_pin(self, pin: int) -> int:
		self.arduino.write(bytes([READ, pin]))
		return int.from_bytes(self.arduino.read(4), byteorder='big')

class ValveController:
	def __init__(self, arduino: Microcontroller):
		self.arduino = arduino

	def set_pin(self, pin: int, value: int):
		self.arduino.write(bytes([SET_PIN, pin, value]))
