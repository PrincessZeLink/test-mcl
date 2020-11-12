from Microcontroller import Arduino, Microcontroller, SimulatedArduino, ValveController


class ValveActuation:
	def __init__(self, type, priority):
		self.type = type
		self.priority = priority

class Valve:
	def __init__(self, type, location, pin, natural, special):
		self.type = type
		self.location = location
		self.pin = pin
		self.natural = natural
		self.special = special
		self.state = None
		self.actuation: ValveActuation = None

	def to_json(self):
		return {
			"type": self.type,
			"location": self.location,
			"natural": self.natural,
			"special": self.special,
			"state": self.state,
			"actuation": self.actuation
		}
		
	@classmethod
	def from_config(cls, config, type, location):
		pin = config['pin']
		natural = config['natural']
		special = config['special']
		return cls(type, location, pin, natural, special)

class ValveMap:
	def __init__(self, address, baud, send_interval, valve_dict, microcontroller):
		self.address = address
		self.baud = baud
		self.send_interval = send_interval
		self.valve_dict = valve_dict
		self.controller: ValveController = microcontroller

	def get(self, valve_type, valve_location) -> Valve:
		return self.valve_dict[valve_type][valve_location]

	def set_actuation(self, valve_type, valve_location, actuation):
		pin = self.get(valve_type, valve_location).pin
		self.controller.set_pin(pin, actuation)

	@classmethod
	def from_config(cls, valves_config, arduino_type):
		address = valves_config['address']
		baud = valves_config['baud']
		send_interval = valves_config['send_interval']

		microcontroller: Microcontroller = None
		
		if arduino_type == 'real':
			microcontroller = Arduino('sensors', address, baud)
		else:
			microcontroller = SimulatedArduino('sensors', address, baud)

		config_valves = valves_config['list']
		valve_dict = {}
		for type, locations in config_valves.items():
			valve_dict[type] = {}
			for location, valve_config in locations.items():
				valve_dict[type][location] = Valve.from_config(valve_config, type, location)

		return cls(address, baud, send_interval, valve_dict, microcontroller)
