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
	def __init__(self,ftp_creds_filename,local_dir_www,log_directory,ftp_log_max_count,ftp_timeout):
		self.scan_delay = 1.1		# delay in seconds between each scan (not incl sensor responce times)
		self.max_scans = 3.11			# number of scans to do, set to zero to scan for ever (until type "ctrl C")
									# by setting this to 3 ensures program stops after few scans id a new config file was made.
		self.log_directory = log_directory	# where to send log files both temp control and processor temp logging
		self.local_dir_www = local_dir_www # default value for local folder
		#self.sensor_config_filename = "sensor_data.csv"
		self.ftp_creds_filename = ftp_creds_filename	# 
		#self.delay_limit = 2		# Number of Seconds delay between temperature scans
		#self.delay_increment =  2		# Number of scans to do, Zero for only stopped by Ctrl C on Keyboard
		self.ftp_log_max_count = ftp_log_max_count  # max scans before sending data to log file
		self.ftplog = 0		# Number of Value Changes before Log File is Saved to remote website, 0 means every change
		#self.heaterIP0 = "0"		# IP for First Heater, zero value indicates not using smart plugs
		#self.heaterIP0_power_scale = 1.0 # newer smartplugs have 1000 x scaling for power info (so scaling needed is 0.001)
		#self.heaterIP1 = "0"		# IP for Second Heater, zero value indicates not using smart plugs
		#self.heaterIP1_power_scale = 1.0
		#self.heaterIP2 = "0"
		#self.heaterIP1_power_scale = 1.0
		#self.heaterIP3 = "0"
		#self.heaterIP3_power_scale = 1.0
		#self.sensor4readings = '0315a80584ff'  #The code for the sensor to be used to measure room temperature
		self.change4log = float(0.6) # change in temperature required before logging and displaying etc
		#self.control_hysteresis = float(6)
		#self.default_target = float(69) # Initial Default temperature target e.g for Sauna
		#self.default_target_full_power = float(64) # Initial value
		#self.max_target = float(18) # default minimum target
		#self.min_target = float(7) # default max target
		#self.precision = float(12) # default precision is 12 bit
		#self.target_integral = float(0.05) # rate of change of offset		    
		#self.one_heater_select = 1
		#self.percent_full_power = 100
		#self.watchdog_time = 200
		self.ftp_timeout = ftp_timeout
		self.log_buffer_flag = True
		self.text_buffer_length = 15

		
		# These parameters are not saved to the config file
		# First three use the program pathname	
		self.prog_path = path.dirname(path.realpath(__file__)) + "/"
		self.prog_name = str(sys_argv[0][:-3])
		self.config_filename = self.prog_name + "_config.cfg"
		print("Program Name is : ",self.prog_name)
		print("config file is : ",self.config_filename)
		self.html_filename = ""
		self.log_filename = ""
		self.log_filename_save_as = ""
		self.local_www_html_filename = ""
		self.log_on = False
		self.temp_log_on = False
		self.log_outfile = ""
		self.temp_log_outfile = ""
		self.scan_count = 0
		self.ftplog_count = 0
		self.temp_ftplog_count = 0
		self.last_ftplog = 0
		self.ref_sensor_index = 0
		self.dbug = False
		self.dbug_ftp = False
		self.exit_flag = False
		self.new_config_wanted = False

	def read_file(self):
		here = "config.read_file"
		config_read = RawConfigParser()
		config_read.read(self.config_filename)
		self.scan_delay = float(config_read.get('SetUp', 'scan_delay')) 
		self.max_scans = float(config_read.get('SetUp', 'max_scans'))
		self.log_directory = config_read.get('SetUp', 'log_directory')
		self.local_dir_www = config_read.get('SetUp', 'local_dir_www')
		self.ftp_creds_filename = config_read.get('SetUp', 'ftp_creds_filename') 
		self.ftp_log_max_count = float(config_read.get('SetUp', 'ftp_log_max_count'))
		self.ftp_timeout =  float(config_read.get('SetUp', 'ftp_timeout'))
		self.log_buffer_flag = config_read.getboolean('SetUp', 'log_buffer_flag')
		self.text_buffer_length  = int(config_read.get('SetUp', 'text_buffer_length'))
		return

	def write_file(self):
		here = "config.write_file"
		config_write = RawConfigParser()
		config_write.add_section('SetUp')
		config_write.set('SetUp', 'scan_delay',self.scan_delay)
		config_write.set('SetUp', 'max_scans',self.max_scans)
		config_write.set('SetUp', 'log_directory',self.log_directory)
		config_write.set('SetUp', 'local_dir_www',self.local_dir_www)
		config_write.set('SetUp', 'ftp_creds_filename',self.ftp_creds_filename)
		config_write.set('SetUp', 'ftp_log_max_count',self.ftp_log_max_count)
		config_write.set('SetUp', 'change4log',self.change4log)
		config_write.set('SetUp', 'ftp_timeout',self.percent_full_power)
		config_write.set('SetUp', 'log_buffer_flag',self.log_buffer_flag)
		config_write.set('SetUp', 'text_buffer_length',self.text_buffer_length)
		# Writing our configuration file to 'self.config_filename'
		pr(self.dbug, here, "ready to write new config file with default values: " , self.config_filename)
		with open(self.config_filename, 'w+') as configfile:
			config_write.write(configfile)
		return 0

