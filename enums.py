from enum import IntEnum


class SensorStatus(IntEnum):
	CRITICALLY_HIGH = 2
	SUSPICIOUSLY_HIGH = 1
	SAFE = 0
	SUSPICIOUSLY_LOW = -1
	CRITICALLY_LOW = -2

class LogPriority(IntEnum):
	INFO = 0
	WARN = 1
	CRITICAL = 0
