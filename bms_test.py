#!python2-32

from __future__ import print_function

from time import sleep
from math import log
import PySwim as swim

PBODR = 0x5005
PBIDR = 0x5006
PBDDR = 0x5007
PBCR1 = 0x5008
PBCR2 = 0x5009

SDA = 0x40
SCL = 0x80


ntc2deg = (7752, 7349, 6970, 6613, 6277, 5960, 5662, 5381, 5115,
4865, 4629, 4405, 4194, 3995, 3807, 3628, 3460, 3300,
3149, 3006, 2870, 2741, 2619, 2503, 2393, 2289, 2190,
2096, 2006, 1921, 1841, 1764, 1690, 1621, 1554, 1491,
1431, 1373, 1319, 1266, 1217, 1169, 1124, 1080, 1039,
1000, 962, 926, 891, 858, 826, 796, 767, 740, 713,
688, 663, 640, 617, 596, 575, 556, 537, 518, 501,
484, 468, 453, 438, 423, 410, 396, 384, 371, 360,
348, 337, 327, 317, 307, 298, 289, 280, 271, 263,
255, 248, 241, 234, 227, 220, 214, 208, 202, 196,
191, 185, 180, 175, 170, 166, 161, 157, 153, 149,
145, 141, 137, 134, 130, 127, 123, 120, 117, 114,
111, 109, 106, 103, 101)


def crc8update(prev, val):
	dat = prev ^ val
	for i in range(8):
		if dat & 0x80:
			dat<<=1
			dat ^= 0x07
		else:
			dat<<=1
	return dat & 0xFF


class swi2c(object):
	def __init__(self, swim):
		self.swim = swim
		# init GPIOs
		self.swim.WriteByte(PBODR, SCL | SDA)
		self.swim.WriteByte(PBDDR, SCL | SDA)
		self.swim.WriteByte(PBCR1, 0)
		self.swim.WriteByte(PBCR2, SCL | SDA)
		self.swim.WriteByte(PBODR, SCL)
		for i in range(10):
			self.swim.WriteByte(PBODR, 0)
			self.swim.WriteByte(PBODR, SCL)
		self.swim.WriteByte(PBODR, SCL | SDA)
					
	def start(self):
		self.swim.WriteByte(PBODR, SCL)	# SDA low while SCL hi
		self.swim.WriteByte(PBODR, 0)	# both low

	def stop(self):
		self.swim.WriteByte(PBODR, SCL)	# SDA low while SCL hi
		self.swim.WriteByte(PBODR, SCL | SDA)	# both hi

	def restart(self):
		self.swim.WriteByte(PBODR, SDA)
		self.swim.WriteByte(PBODR, SCL | SDA)
		self.start()

	def WriteByte(self, val):
		"""expect: SCL low"""
		for i in range(8):
			dat = SDA if val & 0x80 else 0
			self.swim.WriteByte(PBODR, dat)
			self.swim.WriteByte(PBODR, dat | SCL)
			self.swim.WriteByte(PBODR, dat)
			val<<=1
		self.swim.WriteByte(PBODR, SDA)
		self.swim.WriteByte(PBODR, SCL | SDA)
		ack = (self.swim.ReadByte(PBIDR) & SDA)==0
		self.swim.WriteByte(PBODR, SDA)
		return ack

	def ReadByte(self, ack=True):
		val = 0
		for i in range(8):
			val<<=1
			self.swim.WriteByte(PBODR, SDA)
			self.swim.WriteByte(PBODR, SDA | SCL)
			if (self.swim.ReadByte(PBIDR) & SDA)!=0:
				val |= 1
			self.swim.WriteByte(PBODR, SDA)
		dat = 0 if ack else SDA
		self.swim.WriteByte(PBODR, dat)
		self.swim.WriteByte(PBODR, SCL | dat)
		self.swim.WriteByte(PBODR, dat)
		return val

############################################################
# BQ regs

SYS_STAT    = 0
CELLBAL1    = 1
CELLBAL2    = 2
CELLBAL3    = 3
SYS_CTRL1   = 4
SYS_CTRL2   = 5
PROTECT1    = 6
PROTECT2    = 7
PROTECT3    = 8
OV_TRIP     = 9
UV_TRIP     = 0xA
CC_CFG      = 0xB
VC1_HI      = 0xC
VC1_LO      = 0xD
VC2_HI      = 0xE
VC2_LO      = 0xF
VC3_HI      = 0x10
VC3_LO      = 0x11
VC4_HI      = 0x12
VC4_LO      = 0x13
VC5_HI      = 0x14
VC5_LO      = 0x15
VC6_HI      = 0x16
VC6_LO      = 0x17
VC7_HI      = 0x18
VC7_LO      = 0x19
VC8_HI      = 0x1A
VC8_LO      = 0x1B
VC9_HI      = 0x1C
VC9_LO      = 0x1D
VC10_HI     = 0x1E
VC10_LO     = 0x1F
VC11_HI     = 0x20
VC11_LO     = 0x21
VC12_HI     = 0x22
VC12_LO     = 0x23
VC13_HI     = 0x24
VC13_LO     = 0x25
VC14_HI     = 0x26
VC14_LO     = 0x27
VC15_HI     = 0x28
VC15_LO     = 0x29
BAT_HI      = 0x2A
BAT_LO      = 0x2B
TS1_HI      = 0x2C
TS1_LO      = 0x2D
TS2_HI      = 0x2E
TS2_LO      = 0x2F
TS3_HI      = 0x30
TS3_LO      = 0x31
CC_HI       = 0x32
CC_LO       = 0x33
ADCGAIN1    = 0x50
ADCOFFSET   = 0x51
ADCGAIN2    = 0x59

BQRegNames = {
0     : 'SYS_STAT',
1     : 'CELLBAL1',  
2     : 'CELLBAL2',  
3     : 'CELLBAL3',  
4     : 'SYS_CTRL1', 
5     : 'SYS_CTRL2', 
6     : 'PROTECT1',  
7     : 'PROTECT2',  
8     : 'PROTECT3',  
9     : 'OV_TRIP',   
0xA   : 'UV_TRIP',   
0xB   : 'CC_CFG',    
0xC   : 'VC1',    
0xD   : 'VC1_LO',    
0xE   : 'VC2',    
0xF   : 'VC2_LO',    
0x10  : 'VC3',    
0x11  : 'VC3_LO',    
0x12  : 'VC4',    
0x13  : 'VC4_LO',    
0x14  : 'VC5',    
0x15  : 'VC5_LO',    
0x16  : 'VC6',    
0x17  : 'VC6_LO',    
0x18  : 'VC7',    
0x19  : 'VC7_LO',    
0x1A  : 'VC8',    
0x1B  : 'VC8_LO',    
0x1C  : 'VC9',    
0x1D  : 'VC9_LO',    
0x1E  : 'VC10',   
0x1F  : 'VC10_LO',   
0x20  : 'VC11',   
0x21  : 'VC11_LO',   
0x22  : 'VC12',   
0x23  : 'VC12_LO',   
0x24  : 'VC13',   
0x25  : 'VC13_LO',   
0x26  : 'VC14',   
0x27  : 'VC14_LO',   
0x28  : 'VC15',   
0x29  : 'VC15_LO',   
0x2A  : 'BAT',   
0x2B  : 'BAT_LO',   
0x2C  : 'TS1',   
0x2D  : 'TS1_LO',   
0x2E  : 'TS2',   
0x2F  : 'TS2_LO',    
0x30  : 'TS3',    
0x31  : 'TS3_LO',    
0x32  : 'CC',     
0x33  : 'CC_LO',     
0x50  : 'ADCGAIN1',  
0x51  : 'ADCOFFSET', 
0x59  : 'ADCGAIN2',  
}

class BQ769x0(object):
	def __init__(self, i2c):
		self.i2c = i2c
		# get ADC calibration
		val = self.ReadRegB(ADCOFFSET)
		self.adc_offset = val if val<128 else val-0x100
		val1 = self.ReadRegB(ADCGAIN1)
		val2 = self.ReadRegB(ADCGAIN2)
		self.adc_gain = 365+((val1<<1) & 0x18)+(val2>>5)
		return
		# ping
		self.WriteRegB(PROTECT3, 0x11)
		val = self.ReadRegB(PROTECT3)
		if val!=0x11:
			raise Exception('AFE INIT ERR 13: PROTECT3 mismatch: %02X' % (val))
		# bring up
		self.WriteRegB(CELLBAL1, 0)		
		self.WriteRegB(CELLBAL2, 0)		
		self.WriteRegB(CELLBAL3, 0)		
		self.WriteRegB(SYS_CTRL1, 0x18)		
		self.WriteRegB(PROTECT1, 0x9A)
		self.WriteRegB(PROTECT2, 0x73)
		self.WriteRegB(PROTECT3, 0x60)
		self.WriteRegB(OV_TRIP, self.mvtoadc(4200))		
		self.WriteRegB(UV_TRIP, self.mvtoadc(2750))		
		self.WriteRegB(CC_CFG, 0x19)
		sleep(0.8)
		self.WriteRegB(SYS_CTRL2, self.ReadRegB(SYS_CTRL2) & 0x3F | 0x20)
		sleep(0.25)
		self.WriteRegB(SYS_STAT, 0xFF)
		sleep(0.25)


	def mvtoadc(self, val):
		return ((((val-self.adc_offset)*1000)/self.adc_gain)>>4) & 0xFF

	def adctomv(self, val):
		if val==0:
			return 0
		return (val*self.adc_gain)//1000+self.adc_offset

	def adctodeg(self, val):
		return self.rtstodeg(self.adctorts(val))
		"""
		vtsx = val*0.382
		rts = 10000.0*vtsx/(3300.0-vtsx)
		tmp = 1.0/(1.0/(273.15+25)+1.0/3435*log(rts/10000.0))
		return (tmp-273.15)*10.0
		"""

	def adctorts(self, val):
		vtsx = (val*391)>>10
		if vtsx>=3000:
			return 10000
		return vtsx*1000//(3300-vtsx)

	def rtstodeg(self, val):
		for ix in range(len(ntc2deg)):
			if val>=ntc2deg[ix]:
				return ix-20
		return -273

	def ReadRegB(self, reg):
		self.i2c.start()
		if not self.i2c.WriteByte(0x10):
			self.i2c.stop()
			raise Exception('WSA nack')
		if not self.i2c.WriteByte(reg):
			self.i2c.stop()
			raise Exception('REG nack')
		self.i2c.restart()
		crc = 0
		if not self.i2c.WriteByte(0x11):
			self.i2c.stop()
			raise Exception('RSA nack')
		crc = crc8update(crc, 0x11)
		val = i2c.ReadByte()
		crc = crc8update(crc, val)
		dev_crc = i2c.ReadByte(False)
		self.i2c.stop()
		if dev_crc!=crc:
			raise Exception('CRC mismatch: got %02X instead of %02X' % (dev_crc, crc))
		return val
		
	def ReadRegW(self, reg):
		self.i2c.start()
		if not self.i2c.WriteByte(0x10):
			self.i2c.stop()
			raise Exception('WSA nack')
		if not self.i2c.WriteByte(reg):
			self.i2c.stop()
			raise Exception('REG nack')
		self.i2c.restart()
		crc = 0
		if not self.i2c.WriteByte(0x11):
			self.i2c.stop()
			raise Exception('RSA nack')
		crc = crc8update(crc, 0x11)
		vh = i2c.ReadByte()
		crc = crc8update(crc, vh)
		dev_crc = i2c.ReadByte()
		if dev_crc!=crc:
			self.i2c.stop()
			raise Exception('H CRC mismatch: got %02X instead of %02X' % (dev_crc, crc))
		crc = 0
		vl = i2c.ReadByte()
		crc = crc8update(crc, vl)
		dev_crc = i2c.ReadByte(False)
		self.i2c.stop()
		if dev_crc!=crc:
			raise Exception('L CRC mismatch: got %02X instead of %02X' % (dev_crc, crc))
		return (vh<<8) | vl

	def WriteRegB(self, reg, val):
		self.i2c.start()
		crc = 0
		if not self.i2c.WriteByte(0x10):
			self.i2c.stop()
			raise Exception('WSA nack')
		crc = crc8update(crc, 0x10)
		if not self.i2c.WriteByte(reg):
			self.i2c.stop()
			raise Exception('REG nack')
		crc = crc8update(crc, reg)
		if not self.i2c.WriteByte(val):
			self.i2c.stop()
			raise Exception('VAL nack')
		crc = crc8update(crc, val)
		if not self.i2c.WriteByte(crc):
			self.i2c.stop()
			raise Exception('CRC nack')
		self.i2c.stop()
		return True		

	def GetCellVoltage(self, cell):
		return self.adctomv(self.ReadRegW(VC1_HI+cell*2))

	def GetTemperature(self, sensor):
		return self.adctodeg(self.ReadRegW(TS1_HI+sensor*2))

if __name__=='__main__':
	from binascii import hexlify

	print(swim.open())
	print('UID:', hexlify(swim.read(0x4926, 12)).upper(), '\n')

	idrs = (0x5001, 0x5006, 0x500B, 0x5010)
	for ix in range(len(idrs)):
		print('P%X_IDR: %02X' % (ix+0xA, swim.ReadByte(idrs[ix])))

	print('\n---- BQ769x0 ----')
	i2c = swi2c(swim)
	bq = BQ769x0(i2c)
	for reg in range(0xC):
		print('%-9s %02X' % (BQRegNames.get(reg, "%02X" % (reg)), bq.ReadRegB(reg)))

	for reg in range(0x0C, 0x34, 2):
		print('%-9s %04X' % (BQRegNames.get(reg, "%02X" % (reg)), bq.ReadRegW(reg)))

	for cell in range(15):
		print('Cell', cell+1, bq.GetCellVoltage(cell))

	for ts in range(3):
		print('TS', ts+1, bq.GetTemperature(ts), 'deg C')

	swim.close()
	