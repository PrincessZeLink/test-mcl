import time
from typing import Dict, List
from Microcontroller import Arduino, Microcontroller, SensorController, SimulatedArduino
from Warning import Warning

SAFE = 'safe'
WARNING = 'warning'
CRITICAL = 'critical'

class Boundaries:
	def __init__(self, safe_boundaries, warn_boundaries):
		self.safe_boundaries = safe_boundaries
		self.warn_boundaries = warn_boundaries

	@classmethod
	def from_config(cls, config):
		return cls(config['safe'], config['warn'])

	def get_safety(self, reading):
		if self.safe_boundaries[0] < reading < self.safe_boundaries[1]:
			return SAFE
		elif self.warn_boundaries[0] < reading < self.warn_boundaries[1]: # idk how the 'warn' array works
			return WARNING
		else:
			return CRITICAL

class Sensor:
	def __init__(self, type, location, kalman_args, boundaries, pin):
		self.kalman_args = kalman_args
		self.boundaries = boundaries
		self.pin = pin
		self.measured_time = None
		self.measured = None
		self.normalized = None
		self.status = None
		self.type = type
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

	def poll(self) -> List[Sensor]:
		warning_sensors = []
		for locations in self.sensor_dict.values():
			for sensor in locations.values():
				value = self.controller.read_pin(sensor.pin)
				sensor.log(value, time.time())
				if sensor.status != SAFE:
					warning_sensors.append(sensor)

		return warning_sensors

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

		
