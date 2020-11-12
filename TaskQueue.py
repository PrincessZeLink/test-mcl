import queue

class TaskQueue:
	def __init__(self, queue_: queue.Queue=None):
		if queue_ is None:
			self.queue_ = queue.Queue()
		else:
			self.queue_ = queue_
		self.status = None

	def empty(self):
		return self.queue_.empty()

	def next(self):
		try:
			return self.queue_.get()
		except queue.Empty:
			return None # TODO do something if the queue is empty

