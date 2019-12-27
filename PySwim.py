from __future__ import print_function

from ctypes import *
from time import sleep

class error(Exception):
	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

err_mode_result = False	# return result code (0-ok, other-error code)
err_mode_raise = True	# raise exception on failure
err_mode = err_mode_raise

def PySwimSuccess(val):
	if val==0:
		return True
	if err_mode==err_mode_result:
		return False
	else:
		raise error(val)			

# import DLL
_Dll = WinDLL("stm_swim.dll")

# low level functions

LP_c_char = POINTER(c_char)
LP_LP_c_char = POINTER(LP_c_char)

_Open = _Dll.DiGdiOpen
_Open.argtypes = [c_uint, c_uint, c_uint, LP_LP_c_char, c_uint]
_Open.restype = PySwimSuccess

_Close = _Dll.DiGdiClose
_Close.argtypes = [c_uint]
_Close.restype = PySwimSuccess

_InitIO = _Dll.DiGdiInitIO
_InitIO.argtypes = [c_uint]
_InitIO.restype = PySwimSuccess

_SetSpeed = _Dll.SwimApi_SetHostSpeedMode
_SetSpeed.argtypes = [c_uint]
_SetSpeed.restype = PySwimSuccess

_MemRead = _Dll.SwimApi_MemoryRead
_MemRead.argtypes = [c_uint, c_char_p, c_uint]
_MemRead.restype = PySwimSuccess

_MemWrite = _Dll.SwimApi_MemoryWrite
_MemWrite.argtypes = [c_uint, c_char_p, c_uint]
_MemWrite.restype = PySwimSuccess

reset = _Dll.SwimApi_Reset
reset.argtypes = [c_uint]
reset.restype = PySwimSuccess

RESET_ENTER = 0
RESET_ONLY = 1
RESET_COMM = 2
RESET_ASSERT = 3
RESET_RELEASE = 4

####################################

def open():
	argc = 1
	argv = (LP_c_char * (argc))()
	argv[0] = create_string_buffer('-stlink3')
	#argv[3] = create_string_buffer('-allmcu')
	#argv[4] = create_string_buffer('-hotplug')
	#argv[0] = create_string_buffer('-SPY3')
	#argv[1] = create_string_buffer('swim.log')
	_Open(0x126, 0x126, argc, argv, 0)
	_InitIO(0)
	reset(RESET_ASSERT)
	reset(RESET_ASSERT)
	reset(RESET_RELEASE)
	reset(RESET_ASSERT)
	reset(RESET_ENTER)
	_SetSpeed(0)
	reset(RESET_ONLY)
	write(0x7F80, '\xA0')
	reset(RESET_RELEASE)
	sleep(0.1)
	read(0x7F99, 1)
	reset(RESET_COMM)
	write(0x7F80, '\xB0')
	_SetSpeed(1)
	write(0x7F80, '\xB4')
	return True


def close():
	reset(RESET_ONLY)
	#reset(RESET_RELEASE)
	return _Close(0)


def write(addr, data):
	return _MemWrite(addr, data, len(data))	


def read(addr, size):
	buf = create_string_buffer(size)
	if _MemRead(addr, buf, size):
		return buf.raw
	else:
		return None


def ReadByte(addr):
	r = read(addr, 1)
	if r:
		return ord(r)
	else:
		return None

def WriteByte(addr, val):
	return write(addr, chr(val))


__all__ = ["open", "close", "write", "read", "ReadByte", "WriteByte", "err_mode", "err_mode_result", "err_mode_raise"]


if __name__=="__main__":
	from binascii import hexlify

	print(open())
	print(hexlify(read(0x4926, 12)).upper())
	print(hexlify(read(0x4FFC, 4)).upper())
	for i in range(0x5000, 0x5014):
		print('%04X: %02X' % (i, ReadByte(i)))
	#raw_input("read")
	close()
