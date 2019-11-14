#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	config_037.py module for the config class
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
#from sys import exit as sys_exit
#import socket

# Third party imports
#from w1thermsensor import W1ThermSensor

# Local application imports
from utility_037 import pr,make_time_text,send_by_ftp


class class_config:
	def __init__(self):
		self.__c_filename = "" # must be set
		self.scan_delay = 1.1		# delay in seconds between each scan (not incl sensor responce times)
		self.max_scans = 3			# number of scans to do, set to zero to scan for ever (until type "ctrl C")
									# by setting this to 3 ensures program stops after few scans id a new config file was made.
		self.log_directory = "log/"		# where to send log files both temp control and processor temp logging
		self.local_dir_www = "/var/www/html/" # default value for local folder
		self.sensor_config_filename = "sensor_data.csv"
		self.ftp_creds_filename = 'ftp_creds.csv'	# 
		self.delay_limit = 2		# Number of Seconds delay between temperature scans
		self.delay_increment =  2		# Number of scans to do, Zero for only stopped by Ctrl C on Keyboard
		self.ftp_log_max_count = 5  # max scans before sending data to log file
		self.ftplog = 0		# Number of Value Changes before Log File is Saved to remote website, 0 means every change
		self.heaterIP0 = "0"		# IP for First Heater, zero value indicates not using smart plugs
		self.heaterIP0_power_scale = 1.0 # newer smartplugs have 1000 x scaling for power info (so scaling needed is 0.001)
		self.heaterIP1 = "0"		# IP for Second Heater, zero value indicates not using smart plugs
		self.heaterIP1_power_scale = 1.0
		self.heaterIP2 = "0"
		self.heaterIP1_power_scale = 1.0
		self.heaterIP3 = "0"
		self.heaterIP3_power_scale = 1.0
		self.sensor4readings = '0315a80584ff'  #The code for the sensor to be used to measure room temperature
		self.change4log = float(0.6) # change in temperature required before logging and displaying etc
		self.control_hysteresis = float(6)
		self.default_target = float(69) # Initial Default temperature target e.g for Sauna
		self.default_target_full_power = float(64) # Initial value
		self.max_target = float(18) # default minimum target
		self.min_target = float(7) # default max target
		self.precision = float(12) # default precision is 12 bit
		self.target_integral = float(0.05) # rate of change of offset		    
		self.one_heater_select = 1
		self.percent_full_power = 100
		self.watchdog_time = 200
		self.ftp_timeout = 10

		
		# These parameters are not saved to the config file
		# First three use the program pathname
		self.prog_path = ""
		self.config_filename = ""
		#  was self.sensor_info_filename = ""  august 9th 2018
		self.s_filename = "" # Set later based on "config.sensor_config_filename" and program path


		self.html_filename = ""

		self.log_filename = ""
		self.temp_log_filename = ""
		self.log_filename_save_as = ""
		self.temp_log_filename_save_as = ""

		self.status_html_filename = ""
		self.log_html_filename = ""
		self.local_www_html_filename = ""
		self.local_www_log_html_filename = "" 
		self.local_www_status_html_filename = "" 
		self.local_www_log_csv = ""
		self.log_on = False
		self.temp_log_on = False
		#self.sensor_presconfig.s_filename =ent = False now a mysensor value
		self.log_outfile = ""
		self.temp_log_outfile = ""
		self.scan_count = 0
		self.ftplog_count = 0
		self.temp_ftplog_count = 0
		self.last_ftplog = 0
		self.ref_sensor_index = 0
		self.heater1_on = 0
		self.heater2_on = 0
		self.one_first = 1
		self.last_target = 0
		self.last_target_full_power = 0
		self.number_seen = 0
		#
		#Flags
		self.underfloor = False
		self.dbug = False # set True by option -d
		self.dbug_w1 = False
		self.dbug_ftp = False
		self.exit_flag = False
		self.new_config_wanted = False
		self.new_sensor_file_wanted = False
		self.sauna = False # sauna mode
		self.use_schedule = True

		#sauna control parameters
		self.sauna_on = 0.0
		self.target_offset = - 1.1
		self.detect_off_count = 0
		self.reached_target = False
		self.my_module_name = __name__
		self.prog_name = "not_set"

	def set_filename(self,c_filename):
		self.__c_filename =  c_filename

	def read_file(self):
		here = "config.read_file"
		config_read = RawConfigParser()
		config_read.read(self.__c_filename)
		self.scan_delay = float(config_read.getint('SetUp', 'scan_delay')) 
		self.max_scans = int(config_read.getint('SetUp', 'max_scans'))
		self.log_directory = config_read.get('SetUp', 'log_directory')
		self.local_dir_www = config_read.get('SetUp', 'local_dir_www')
		self.sensor_config_filename = config_read.get('SetUp','sensor_config_filename')
		self.ftp_creds_filename = config_read.get('SetUp', 'ftp_creds_filename') 
		self.delay_limit = float(config_read.get('SetUp', 'delay_limit'))
		self.delay_increment = float(config_read.get('SetUp', 'delay_increment'))
		self.ftp_log_max_count = float(config_read.get('SetUp', 'ftp_log_max_count'))
		self.heaterIP0 = config_read.get('SetUp', 'heaterIP0')
		self.heaterIP0_power_scale = float(config_read.get('SetUp', 'heaterIP0_power_scale'))
		self.heaterIP1 = config_read.get('SetUp', 'heaterIP1')
		self.heaterIP1_power_scale = float(config_read.get('SetUp', 'heaterIP1_power_scale'))
		self.heaterIP2 = config_read.get('SetUp', 'heaterIP2')
		self.heaterIP2_power_scale = float(config_read.get('SetUp', 'heaterIP2_power_scale'))
		self.heaterIP3 = config_read.get('SetUp', 'heaterIP3')
		self.heaterIP3_power_scale = float(config_read.get('SetUp', 'heaterIP3_power_scale'))
		self.sensor4readingmy_s5ensors = config_read.get('SetUp', 'sensor4readings')
		self.change4log = float(config_read.get('SetUp', 'change4log'))
		self.control_hysteresis = float(config_read.get('SetUp', 'control_hysteresis'))
		self.default_target = float(config_read.get('SetUp', 'default_target'))
		self.default_target_full_power = float(config_read.get('SetUp', 'default_target_full_power'))
		self.max_target = float(config_read.get('SetUp', 'max_target'))
		self.min_target = float(config_read.get('SetUp', 'min_target'))
		self.precision = float(config_read.get('SetUp', 'precision'))
		self.target_integral = float(config_read.get('SetUp', 'target_integral'))
		self.one_heater_select = float(config_read.get('SetUp', 'one_heater_select'))
		self.percent_full_power = float(config_read.get('SetUp', 'percent_full_power'))
		self.watchdog_time = float(config_read.get('SetUp', 'watchdog_time'))
		self.ftp_timeout =  float(config_read.get('SetUp', 'ftp_timeout'))
		return

	def write_file(self):
		here = "config.write_file"
		config_write = RawConfigParser()
		config_write.add_section('SetUp')
		config_write.set('SetUp', 'scan_delay',self.scan_delay)
		config_write.set('SetUp', 'max_scans',self.max_scans)
		config_write.set('SetUp', 'log_directory',self.log_directory)
		config_write.set('SetUp', 'local_dir_www',self.local_dir_www)
		config_write.set('SetUp', 'sensor_config_filename',self.sensor_config_filename)
		config_write.set('SetUp', 'ftp_creds_filename',self.ftp_creds_filename)
		config_write.set('SetUp', 'delay_limit',self.delay_limit)
		config_write.set('SetUp', 'delay_increment',self.delay_increment)
		config_write.set('SetUp', 'ftp_log_max_count',self.ftp_log_max_count)
		config_write.set('SetUp', 'heaterIP0',self.heaterIP0)
		config_write.set('SetUp', 'heaterIP0_power_scale',self.heaterIP0_power_scale)
		config_write.set('SetUp', 'heaterIP1',self.heaterIP1)
		config_write.set('SetUp', 'heaterIP1_power_scale',self.heaterIP1_power_scale)
		config_write.set('SetUp', 'heaterIP2',self.heaterIP2)
		config_write.set('SetUp', 'heaterIP2_power_scale',self.heaterIP2_power_scale)
		config_write.set('SetUp', 'heaterIP3',self.heaterIP3)
		config_write.set('SetUp', 'heaterIP3_power_scale',self.heaterIP3_power_scale)
		config_write.set('SetUp', 'sensor4readings',self.sensor4readings)
		config_write.set('SetUp', 'change4log',self.change4log)
		config_write.set('SetUp', 'control_hysteresis',self.control_hysteresis)
		config_write.set('SetUp', 'default_target',self.default_target)
		config_write.set('SetUp', 'default_target_full_power',self.default_target_full_power)
		config_write.set('SetUp', 'max_target',self.max_target)
		config_write.set('SetUp', 'min_target',self.min_target)
		config_write.set('SetUp', 'precision',self.precision)
		config_write.set('SetUp', 'target_integral',self.target_integral)
		config_write.set('SetUp', 'one_heater_select',self.one_heater_select)
		config_write.set('SetUp', 'percent_full_power',self.percent_full_power)
		config_write.set('SetUp', 'watchdog_time',self.percent_full_power)
		config_write.set('SetUp', 'ftp_timeout',self.percent_full_power)
		# Writing our configuration file to 'c_filename'
		pr(self.dbug, here, "ready to write new config file withdefault values: " , self.__c_filename)
		with open(self.__c_filename, 'w+') as configfile:
			config_write.write(configfile)
		return 0

