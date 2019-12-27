# PySWIM
STM8 SWIM access library, BMS tester

This library is a simple ctypes wrapper for ST's DLLs. 

## Functions implemented:
* SWIM init
* Read memory
* Write memory

## Requirements
* Python 2
* ST-Link

## BMS tester
bms_test.py is a tester script for Ninebot/Xiaomi BMSes based on STM8L151K6+BQ769x0.

### Functions
* STM8 GPIO regs dump
* BQ raw regs dump
* BQ cell voltages dump
* BQ temperature sensors dump

### Howto
Connect ST-Link to BMS and to PC, press start button on the BMS to wake it up, run the script.
