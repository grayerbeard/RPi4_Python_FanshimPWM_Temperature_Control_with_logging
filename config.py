#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	cpu_monitor_config.py module for the config class
#   testing in shed version OK in sauna
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
from configparser import RawConfigParser
from csv import DictReader as csv_DictReader
from csv import DictWriter as csv_DictWriter
#from datetime import datetime
#from shutil import copyfile
#from ftplib import FTP
#from sys import argv as sys_argv
from sys import exit as sys_exit
#import socket
from os import path
from sys import argv as sys_argv

# Third party imports
#from w1thermsensor import W1ThermSensor

# Local application imports
from utility import pr,make_time_text,send_by_ftp


class class_config:
	def __init__(self):
# Start of items set in config.cfg
	# Scan
		self.scan_delay = 10		# delay in seconds between each scan (not incl sensor responce times)
		self.max_scans = 0			# number of scans to do, set to zero to scan for ever (until type "ctrl C")
	# Log
		self.log_directory = "log/"	# where to store log files
		self.local_dir_www = "/var/www/html/" # default value for local web folder
		self.log_buffer_flag = True	 # whether to generate the csv log file as well as the html text file	
		self.text_buffer_length = 15	# number of lines in the text buffer in the html file	
	# Ftp
		self.ftp_creds_filename = "/home/pi/ftp_creds/ftp_creds.csv"
		self.ftp_log_max_count  = 5
		self.ftp_timeout = 0.5
		self.ftplog = 0		# Number of Value Changes before Log File is Saved to remote website, 0 means every change
	# Fan
		self.max_temp =  69.0
		self.min_temp = 61.0 
		self.min_speed = 75
		self.max_speed = 90
		self.min_freq = 2.0
		self.max_freq = 5.0
		self.brightness = 80
# End of items set in config.cfg	

# Start of parameters are not saved to the config file
		# Based on the program name work out names for other files
		# First three use the program pathname	
		self.prog_path = path.dirname(path.realpath(__file__)) + "/"
		self.prog_name = str(sys_argv[0][:-3])
		self.config_filename = "config.cfg"
		print("Program Name is : ",self.prog_name)
		print("config file is : ",self.config_filename)

	def read_file(self):
		here = "config.read_file"
		config_read = RawConfigParser()
		config_read.read(self.config_filename)
		section = "Scan"
		self.scan_delay = float(config_read.get(section, 'scan_delay')) 
		self.max_scans = float(config_read.get(section, 'max_scans'))
		section = "Log"
		self.log_directory = config_read.get(section, 'log_directory')
		self.local_dir_www = config_read.get(section, 'local_dir_www')
		self.log_buffer_flag = config_read.getboolean(section, 'log_buffer_flag')
		self.text_buffer_length  = int(config_read.get(section, 'text_buffer_length'))		
		section = "Ftp"
		self.ftp_creds_filename = config_read.get(section, 'ftp_creds_filename') 
		self.ftp_log_max_count = float(config_read.get(section, 'ftp_log_max_count'))
		section = "Fan"		
		self.max_temp =  float(config_read.get(section, 'max_temp'))
		self.min_temp =  float(config_read.get(section, 'min_temp'))
		self.min_speed =  float(config_read.get(section, 'min_speed'))
		self.max_speed =  float(config_read.get(section, 'max_speed'))
		self.min_freq =  float(config_read.get(section, 'min_freq'))
		self.max_freq =  float(config_read.get(section, 'max_freq'))
		self.brightness =  float(config_read.get(section, 'brightness'))
		return

	def write_file(self):
		here = "config.write_file"
		config_write = RawConfigParser()
		section = "Scan"
		config_write.add_section(section)
		config_write.set(section, 'scan_delay',self.scan_delay)
		config_write.set(section, 'max_scans',self.max_scans)
		section = "Log"
		config_write.add_section(section)
		config_write.set(section, 'log_directory',self.log_directory)
		config_write.set(section, 'local_dir_www',self.local_dir_www)
		config_write.set(section, 'log_buffer_flag',self.log_buffer_flag)
		config_write.set(section, 'text_buffer_length',self.text_buffer_length)	
		section = "Ftp"
		config_write.add_section(section)
		config_write.set(section, 'ftp_creds_filename',self.ftp_creds_filename)
		config_write.set(section, 'ftp_log_max_count',self.ftp_log_max_count)
		section = "Fan"	
		config_write.add_section(section)	
		config_write.set(section, 'max_temp',self.max_temp)
		config_write.set(section, 'min_temp',self.min_temp)
		config_write.set(section, 'min_speed',self.min_speed)
		config_write.set(section, 'max_speed',self.max_speed)		
		config_write.set(section, 'min_freq',self.min_freq)
		config_write.set(section, 'max_freq',self.max_freq)
		config_write.set(section, 'brightness',self.max_freq)			
		
		# Writing our configuration file to 'self.config_filename'
		pr(self.dbug, here, "ready to write new config file with default values: " , self.config_filename)
		with open(self.config_filename, 'w+') as configfile:
			config_write.write(configfile)
		return 0

