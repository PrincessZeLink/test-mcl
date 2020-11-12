import time
from threading import Thread
from queue import Queue

from Task import Task
from Stage import Stage
from Telemetry import Telemetry
from Valve import ValveMap
from Sensor import SensorMap

class Launch:
	def __init__(self, config):
		self.task_queue = Queue()
		self.arduino_type = config['arduino_type']
		self.telemetry = Telemetry.from_config(config['telemetry'], self.handle_message)
		self.sensors = SensorMap.from_config(config['sensors'], self.arduino_type)
		self.valves = ValveMap.from_config(config['valves'], self.arduino_type)
		self.delay = config['timer']['delay']
		self.start_time = None
		self.hard_abort = False
		self.soft_abort = False
		self.task_executor = Thread(target=self.execute_tasks, daemon=True)
		self.stage = Stage('stage_1')

	def execute_task(self, task: Task):
		"""
		Main task handler
		"""
		if task.action == 'reset_telemetry':
			self.telemetry.reset()
		elif task.action == 'set_valve_actuation':
			valve_type = task.payload['type']
			valve_location = task.payload['location']
			valve_actuation = task.payload['actuation']
			self.valves.set_actuation(valve_type, valve_location, valve_actuation)

	def execute_tasks(self):
		while not self.hard_abort and not self.soft_abort:
			# 'blocking' is ok here because it's in its own thread
			task = self.task_queue.get(block=True)
			self.execute_task(task)

	def handle_message(self, type, payload):
		if type == 'hard_abort':
			self.hard_abort = True
		elif type == 'soft_abort':
			self.soft_abort = True
		elif type == 'cancel_soft_abort':
			self.soft_abort = False
		elif type == 'set_valve':
			valve_type = payload.get("type")
			valve_location = payload.get("location")
			valve_actuation = payload.get("actuation")
			self.valves.set_actuation(valve_type, valve_location, valve_actuation)

	def run(self):
		self.start_time = time.time()
		self.task_executor.start()
		
		while True:
			warning_sensors = self.sensors.poll()
			for sensor in warning_sensors:
				self.telemetry.warn('sensor', sensor.to_json())

			self.telemetry.log('sensors', self.sensors.to_json())

			time.sleep(self.delay)

if __name__ == "__main__":
	import json
	config_file = open("config.json")
	config = json.load(config_file)
	config_file.close()
	launch = Launch(config)
	launch.run()
