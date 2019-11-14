#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	smartplug.py
#  
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNimport sys, getoptESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#  
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#	MA 02110-1301, USA.

# Standard library imports
#from configparser import RawConfigParser
from csv import DictReader as csv_DictReader
from csv import DictWriter as csv_DictWriter
from datetime import datetime
from shutil import copyfile
from ftplib import FTP
from sys import argv as sys_argv
from sys import exit as sys_exit
import socket

# Third party imports
from w1thermsensor import W1ThermSensor

# Local application imports
from utility import pr,make_time_text,send_by_ftp

class class_smartplug():
	def __init__(self,number_of_plugs):
							# NOTE Set for 2 plugs,  
							# must introduce way to set number if need more 
		self.seen = [False]*number_of_plugs
		self.state  = [1.234]*number_of_plugs		# state on is "1" off "0"
		self.ip = ["not set"]*number_of_plugs 			# ip address
		self.heater_power_scale =[1]*number_of_plugs # required as newer plugs have different scale 
		self.current = [1.234]*number_of_plugs 		# current
		self.voltage = [1.234]*number_of_plugs  	# voltage
		self.power = [1.234]*number_of_plugs 		# power now
		self.total = [1.234]*number_of_plugs 		# total power (today ?)
		self.error = [1.234]*number_of_plugs 		# error code
		self.sent = ["command"]*number_of_plugs		# last command sent
		self.info_received = ["error"]*number_of_plugs	# last info reply received
		self.read_received = ["error"]*number_of_plugs	# last read reply received
		self.cmnd_start = datetime.now()
		self.cmnd_end = datetime.now()
		self.max_time = -1
		self.timeout = -1
		self.status_text_error_count = 0
		self.print_out_error_count = 0
		self.get_status_error_count = 0
		self.turn_off_time_taken = -2.34
		self.turn_on_time_taken = -2.34
		self.do_info_time_taken = -2.34
		self.do_read_time_taken = -2.34
		self.dbug = False # Flag, set True if want debug messages
		# Predefined Smart Plug Commands
		# For a full list of commands, consult tplink_commands.txt
		self.commands = {'info'     : '{"system":{"get_sysinfo":{}}}',
			'on'       : '{"system":{"set_relay_state":{"state":1}}}',
			'off'      : '{"system":{"set_relay_state":{"state":0}}}',
			'read'     : '{"emeter":{"get_realtime":{}}}' 
		}

	def calculate_time(self,where):
		timedelta = self.cmnd_end - self.cmnd_start
		micro_time = timedelta.microseconds
		if micro_time > self.max_time:
			self.max_time = micro_time
		if micro_time > 0.5 * self.timeout:
			self.timeout = 1.1 * self.timeout
			#-# print("After : ",where, " Timeout increased to : ",round((self.timeout/1000000),4), \
			#-#	  "Because delay was ",round((micro_time/1000000),4))
		elif micro_time < (0.2*self.timeout) and self.timeout>750000:
			self.timeout = 0.95 * self.timeout
			#-# print("After : ",where, " Timeout decreased to : ",round((self.timeout/1000000),4),  \
			#-#   "Because delay was ",round((micro_time/1000000),4))
		return micro_time


	def validIP(self,ip):
		pieces = ip.split('.')
		if len(pieces) != 4: return False
		try: return all(0<=int(p)<256 for p in pieces)
		except ValueError: return False

	def turn_on_smartplug(self,index):
		here = "turn_on_smartplug"
		cmd = self.commands["on"]
		# print("on called : ",index)	
		try:
			if self.ip[index] == "not set":
				pr(self_dbug,here,"Smart Plug no ip address for Index : ", index)	
			else:
				pr(self.dbug,here, "Smart Plug cmd and index : ", str(cmd) + " : " + str(self.ip[index]))
				responce = self.send_command(cmd,self.ip[index],9999,False)
				pr(self.dbug,here,"Index, IP, On responce : ", str(index) + " : " +
					self.ip[index] + " : " + responce) 
				return responce
		except:
			return "error"

	def turn_off_smartplug(self,index):
		here = "turn_off_smartplug"
		cmd = self.commands["off"]
		# print("off called : ",index)
		try:
			if self.ip[index] == "not set":
				pr(self_dbug,here, "Smart Plug no ip address for Index : ", index)
			else:
				pr(self.dbug,here, "Smart Plug cmd and index : ", str(cmd) + " : " + str(self.ip[index]))
				responce = self.send_command(cmd,self.ip[index],9999,False)
				pr(self.dbug,here,"Index, IP, Off responce : ", str(index) + " : " +  
					self.ip[index] + " : " +  responce) 
				return responce
		except:
			return "error"

	# Encryption and Decryption of TP-Link Smart Home Protocol
	# XOR Autokey Cipher with starting key = 171
	#revied code refer https://github.com/softScheck/tplink-smartplug/issues/20 
	def encrypt(self,string):
		key = 171
		result = b"\0\0\0"+ chr(len(string)).encode('latin-1')
		for i in string.encode('latin-1'):
			a = key ^ i
			key = a
			result += chr(a).encode('latin-1')
		return result

	def decrypt(self,string):
		key = 171 
		result = ""
		for i in string: 
			a = key ^ i
			key = i 
			result += chr(a)
		return result
	
	def get_json(self,string,value):
		try:
			pos = string.find(":",string.find(value))
			if pos == -1 :
				return -1
			else:	
				end1 = string.find(",",pos)
				end2 = string.find("}",pos)	
			try:
				return float(string[pos+1:end1])
			except:
				try:
					return float(string[pos+1:end2])
				except:
					return -1
		except: return -99 

	def  send_command(self,cmded,ip,port,dbug_flag) :
		here = "743 smartplug send command"
		pr(dbug_flag,here,"command and ip : ", str(cmded) + " : " + str(ip)) 
		try:
			self.cmnd_start = datetime.now()
			sock_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock_tcp.settimeout(self.timeout/1000000)
			sock_tcp.connect((ip, port))
			sock_tcp.send(self.encrypt(cmded))
			data = sock_tcp.recv(2048)
			sock_tcp.close()
			return self.decrypt(data[4:])
		except:
			return "error"
		
	def get_smartplug_status(self,dbug_flag,config):
		here = "get_smartplug_status"
		read_cmd = self.commands["read"]
		info_cmd = self.commands["info"]
		read_results = ["not set"]*config.number_heaters
		info_results = ["not set"]*config.number_heaters
		self.get_status_error_count = 0
		for index in range(0,config.number_heaters,1):
			# print("###### getting status index :",index, "config.number_heaters : ",config.number_heaters)
			if self.ip[index] == "not set":
				pr(dbug_flag,here, "Smart Plug no ip address for Index : ", index)
			else:
				read_results[index] = self.send_command(read_cmd,self.ip[index],9999,dbug_flag)
				if read_results[index] == "error":
					pr(True,here,"Error connecting for read index: " + str(index), " IP : " + self.ip[index])
					read_results[index] = "error"
					self.get_status_error_count += 1
				else:
					self.do_read_time_taken = self.calculate_time("Do Read")
					##pr(True,here,"Result for Read Index : " + str(index), read_results[index])
					pr(dbug_flag,here,"Result for Read Index : " + str(index), read_results[index])
					self.read_received[index] = read_results[index]
					self.current[index] = self.get_json(read_results[index],"current")
					self.voltage[index] = self.get_json(read_results[index],"voltage")
					self.power[index] = self.get_json(read_results[index],"power") * self.heater_power_scale[index]
					self.total[index] = self.get_json(read_results[index],"total")
				info_results[index] = self.send_command(info_cmd,self.ip[index],9999,dbug_flag)  
				if info_results[index] == "error":
					pr(True,here,"Error connecting for info index: " + str(index), " IP : " + self.ip[index])
					info_results[index] = "error"
					self.get_status_error_count += 1
				else:
					self.do_info_time_taken = self.calculate_time("Do Info")
					pr(dbug_flag,here,"Result for Info Index : " + str(index), info_results[index])
					##pr(True,here,"Result for Info Index : " + str(index), info_results[index])
					self.state[index] = self.get_json(info_results[index],"relay_state")
					self.error[index] = self.get_json(info_results[index],"err_code")
					pr(dbug_flag,here, "Relay, Volts, Amps, Power, Total Power & Error Code for Plug : " +  str(self.ip[index]), 
						str(self.state[index])    + " : "    + str(self.voltage[index]) + " : " + 
						str(self.current[index])  + " : "    + str(self.power[index])  + " : " + 
						str(self.total[index])    + " : "    + str(self.error[index]) )
					self.sent[index] = " Read: " + read_cmd + " : Info: " + info_cmd
					self.info_received[index] = info_results[index]
		if self.get_status_error_count == 0:
			return "Got Status OK"
		else:
			return "error"


