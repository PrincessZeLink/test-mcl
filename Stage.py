from typing import List


class Stages:
	def Stages(self, stage_list, send_interval, request_interval):
		self.stage_list: List[str] = stage_list
		self.send_interval: float = send_interval
		self.request_interval: float = request_interval

	@classmethod
	def from_config(cls, config):
		stage_list = config['list']
		send_interval = config['send_interval']
		request_interval = config['request_interval']
		return cls(stage_list, send_interval, request_interval)

class Stage:
	def __init__(self, stage, status=0):
		self.stage = stage
		self.status = status
