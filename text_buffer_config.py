#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	text_buffer_config.py

#   testing in shed version OK in saunalog_directory
#  
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the Licenselog_directory, or
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
from os import path
from sys import argv as sys_argv
#from datetime import datetime
#from shutil import copyfile
#from ftplib import FTP
#from sys import argv as sys_argv
#from sys import exit as sys_exit
#import socket

# Third party imports
#from w1thermsensor import W1ThermSensor

# Local application imports
from utility import pr,make_time_text,send_by_ftp


class class_config:
	def __init__(self,ftp_creds_filename,local_dir_www,log_directory,ftp_log_max_count,ftp_timeout):
		self.scan_delay = 10		# delay in seconds between each scan (not incl sensor responce times)
		self.max_scans = 0			# number of scans to do, set to zero to scan for ever (until type "ctrl C")
									# by setting this to 3 ensures program stops after few scans id a new config file was made.
		self.log_directory = log_directory		# where to send log files both temp control and processor temp logging
		self.local_dir_www = local_dir_www # default value for local folder
		self.ftp_creds_filename = ftp_creds_filename	# 
		self.ftp_log_max_count = ftp_log_max_count  # max scans before sending data to log file
		self.ftplog = 0		# Number of Value Changes before Log File is Saved to remote website, 0 means every change
		self.ftp_timeout = ftp_timeout
		self.log_buffer_flag = True

		# These parameters are not saved to the config file
		# First three use the program pathname
		self.prog_path = path.dirname(path.realpath(__file__)) + "/"
		self.prog_name = str(sys_argv[0][:-3])
		self.config_filename = self.prog_name + ".cfg"
		#  was self.sensor_info_filename = ""  august 9th 2018
		#self.log_on = False
		#self.log_outfile = ""
		self.scan_count = 0
		self.ftplog_count = 0
		self.last_ftplog = 0
		self.dbug = False # set True by option -d
		self.dbug_w1 = False
		self.dbug_ftp = False
		self.exit_flag = False
		self.new_config_wanted = False
		
		print("self.ftp_creds_filename : ",self.ftp_creds_filename)

	#def set_filename(self,c_filename):
	#	self.__c_filename =  c_filename

	def read_file(self):
		here = "config.read_file"
		config_read = RawConfigParser()
		config_read.read(self.config_filename)
		self.scan_delay = float(config_read.getint('SetUp', 'scan_delay')) 
		self.max_scans = int(config_read.getint('SetUp', 'max_scans'))
		self.log_directory = config_read.get('SetUp', 'log_directory')
		self.local_dir_www = config_read.get('SetUp', 'local_dir_www')
		self.ftp_creds_filename = config_read.get('SetUp', 'ftp_creds_filename') 
		self.ftp_log_max_count = float(config_read.get('SetUp', 'ftp_log_max_count'))
		self.ftp_timeout =  float(config_read.get('SetUp', 'ftp_timeout'))
		self.log_buffer_flag =  config_read.getboolean('SetUp', 'log_buffer_flag')
		self.a_flag =  config_read.getboolean('SetUp', 'a_flag')
		self.b_flag =  config_read.getboolean('SetUp', 'b_flag')
		self.c_flag =  config_read.getboolean('SetUp', 'c_flag')
		self.d_flag =  config_read.getboolean('SetUp', 'd_flag')
		self.e_flag =  config_read.getboolean('SetUp', 'e_flag')
		print("log_buffer_flag = True",log_buffer_flag)
		print("a_flag = False",self.a_flag)
		print("b_flag = 1",self.b_flag)
		print("b_flag = 0",self.c_flag)
		print("c_flag = Yes",self.d_flag)
		print("d_flag = no",self.e_flag)
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

		config_write.set('SetUp', 'ftp_timeout',self.ftp_timeout)
		# Writing our configuration file to 'config_filename'
		pr(self.dbug, here, "ready to write new config file withdefault values: " , self.config_filename)
		with open(self.config_filename, 'w+') as configfile:
			config_write.write(configfile)
		return 0

