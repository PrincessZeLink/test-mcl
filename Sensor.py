import time
from typing import Dict, Literal
from Microcontroller import Arduino, SensorController, SimulatedArduino
from enums import SensorStatus

class Boundaries:
	def __init__(self, safe_boundaries, warn_boundaries):
		self.safe_boundaries = safe_boundaries
		self.warn_boundaries = warn_boundaries

	@classmethod
	def from_config(cls, config):
		return cls(config['safe'], config['warn'])

	def get_safety(self, reading) -> SensorStatus:
		lower_safe, upper_safe = self.safe_boundaries
		lower_warn, upper_warn = self.warn_boundaries

		if lower_safe <= reading <= upper_safe:
			return SensorStatus.SAFE
		
		if lower_warn <= reading < lower_safe:
			return SensorStatus.SUSPICIOUSLY_LOW
		elif reading < lower_warn:
			return SensorStatus.CRITICALLY_LOW

		if upper_warn >= reading > upper_safe:
			return SensorStatus.SUSPICIOUSLY_HIGH
		elif reading > upper_warn:
			return SensorStatus.CRITICALLY_HIGH

class Sensor:
	def __init__(self, type, location, kalman_args, boundaries, pin):
		self.kalman_args = kalman_args
		self.boundaries = boundaries
		self.pin = pin
		self.measured_time = None
		self.measured = None
		self.normalized = None
		self.status: SensorStatus = None
		self.type: Literal['pressure', 'thermocouple'] = type
		self.location = location

	@classmethod
	def from_config(cls, config, type, location):
		kalman_args = config['kalman_args']
		boundaries = Boundaries.from_config(config['boundaries'])
		pin = config['pin']
		return cls(type, location, kalman_args, boundaries, pin)

	def log(self, reading, time):
		self.measured = reading
		self.measured_time = time
		# TODO add normalized here
		self.status = self.boundaries.get_safety(self.measured)

	def to_json(self):
		return {
			"type": self.type,
			"location": self.location,
			"measured_time": self.measured_time,
			"measured": self.measured,
			"normalized": self.normalized,
			"status": self.status
		}

class SensorMap:
	def __init__(self, address, baud, send_interval, sensor_dict, controller):
		self.address = address
		self.baud = baud
		self.send_interval = send_interval
		self.sensor_dict: Dict[str, Dict[str, Sensor]] = sensor_dict
		self.controller: SensorController = controller

	def to_json(self):
		value = {}
		for type, locations in self.sensor_dict.items():
			value[type] = {}
			for location, sensor in locations.items():
				value[type][location] = sensor.to_json()

		return value

	def log(self):
		import random

		for locations in self.sensor_dict.values():
			for sensor in locations.values():
				value = random.randint(15, 510) # self.controller.read_pin(sensor.pin)
				sensor.log(value, time.time())

	def get_sensor(self, type, location) -> Sensor:
		return self.sensor_dict[type][location]

	def get_type(self, type) -> Dict[str, Sensor]:
		return self.sensor_dict[type]

	@classmethod
	def from_config(cls, config, arduino_type):
		address = config['address']
		baud = config['baud']
		send_interval = config['send_interval']

		controller: SensorController = None
		
		if arduino_type == 'real':
			controller = SensorController(Arduino('sensors', address, baud))
		else:
			controller = SensorController(SimulatedArduino('sensors', address, baud))

		config_sensors = config['list']
		sensor_dict = {}
		for type, locations in config_sensors.items():
			sensor_dict[type] = {}
			for location, sensor_config in locations.items():
				sensor_dict[type][location] = Sensor.from_config(sensor_config, type, location)

		return cls(address, baud, send_interval, sensor_dict, controller)

		
