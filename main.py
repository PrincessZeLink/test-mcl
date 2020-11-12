import time
from threading import Thread
from queue import Queue

from enums import SensorStatus
from Task import Task
from Stage import Stage
from Telemetry import Telemetry
from Valve import ValveActuation, ValveMap
from Sensor import SensorMap

class Launch:
	def __init__(self, config):
		self.task_queue: Queue = Queue()
		self.arduino_type: str = config['arduino_type']
		self.telemetry: Telemetry = Telemetry.from_config(config['telemetry'], self.task_queue.put)
		self.sensors: SensorMap = SensorMap.from_config(config['sensors'], self.arduino_type)
		self.valves: ValveMap = ValveMap.from_config(config['valves'], self.arduino_type)
		self.delay: float = config['timer']['delay']
		self.start_time: float = None
		self.hard_abort: bool = False
		self.soft_abort: bool = False
		self.task_executor: Thread = Thread(target=self.execute_tasks, daemon=True)
		self.stage: Stage = Stage('stage_1')

	def execute_task(self, task: Task):
		"""
		Main task handler
		"""
		if task.action == 'reset_telemetry':
			self.telemetry.reset()
		elif task.action == 'set_valve_actuation':
			type = task.payload['type']
			location = task.payload['location']
			actuation = task.payload['actuation']
			self.valves.set_actuation(type, location, actuation)
		elif task.action == 'hard_abort':
			self.hard_abort = True
		elif task.action == 'soft_abort':
			self.soft_abort = True
		elif task.action == 'cancel_soft_abort':
			self.soft_abort = False

	def execute_tasks(self):
		while not self.hard_abort and not self.soft_abort:
			# 'blocking' is ok here because it's in its own thread
			task = self.task_queue.get(block=True)
			self.execute_task(task)

	def check_pressure_sensors(self):
		# Check pressure sensors
		for sensor in self.sensors.get_type('pressure').values():
			# If the sensor's status is unsafe...
			if sensor.status != SensorStatus.SAFE:
				# Warn about the sensor's status
				self.telemetry.warn('sensor', sensor.to_json())

				# If the pressure is critically high...
				if sensor.status == SensorStatus.CRITICALLY_HIGH:
					# Open the pressure relief valve
					self.task_queue.put(Task('set_valve_actuation', {'type': 'solenoid', 'location': 'pressure_relief', 'actuation': ValveActuation(1, 0)}))
			
			# If the sensor's status is fine...
			else:
				# If the pressure relief valve is open...
				if self.valves.get('solenoid', 'pressure_relief').actuation.type == 1:
					# Close the pressure relief valve
					self.task_queue.put(Task('set_valve_actuation', {'type': 'solenoid', 'location': 'pressure_relief', 'actuation': ValveActuation(0, 0)}))
		

	def run(self):
		self.start_time = time.time()
		self.task_executor.start()
		
		while True:
			self.sensors.log()
			self.check_pressure_sensors()
			
			self.telemetry.info('sensors', self.sensors.to_json())

			time.sleep(self.delay)

if __name__ == "__main__":
	import json
	config_file = open("config.json")
	config = json.load(config_file)
	config_file.close()
	launch = Launch(config)
	launch.run()
