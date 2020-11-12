class Stages:
	def __init__(self, stage_config):
		self.stage_list = stage_config['list']
		self.send_interval = stage_config['send_interval']
		self.request_interval = stage_config['request_interval']

