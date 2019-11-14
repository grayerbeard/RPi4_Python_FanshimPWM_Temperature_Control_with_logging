#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	cpu_temp_log.py an adaption of My sensors.py audust 2019 for logging cpu temperature and load
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
#from w1thermsensor import W1ThermSensor

# Local application imports
from utility import pr,make_time_text,send_by_ftp

class class_cpu_temp_log:
	def __init__(self):
		self.dbug = False
		self.__temp_log_filename =  "not set"
		self.__temp_log_filename_save_as = "not_set"
		self.__local_www_temp_log_filename =  "not set"
		self.__ftp_creds =  "not set"
		self.__send_plain_count = 5
		
	def set_temp_log_filename(self,temp_log_filename):
		# local file for logging to
		self.__temp_log_filename = temp_log_filename
		
	def set_temp_log_filename_save_as(self,temp_log_filename_save_as):
		# local file for logging to
		self.__temp_log_filename_save_as = temp_log_filename_save_as
		
	def set_local_www_temp_log_filename(self,local_www_temp_log_filename):
		# local website filename for loggingf filer
		self.__local_www_temp_log_filename = local_www_temp_log_filename

	def set_ftp_creds(self,ftp_creds):
		# creds file used to send logging file 
		self.__ftp_creds = ftp_creds

	def log_to_file(self,config,cpu_bffr_values,cpu_prog_count):
		here = 	"log_cpu_data_to_file"
		#write the time at the start of the line in logging file
	
		if cpu_prog_count == 0: 
			config.temp_log_outfile.write("Time,")
			config.temp_log_outfile.write("Count,")
			config.temp_log_outfile.write("Temp,")
			config.temp_log_outfile.write("Max,")
			config.temp_log_outfile.write("Min,")
			config.temp_log_outfile.write("CPU Load,")
			config.temp_log_outfile.write("CPU Mem,")
			config.temp_log_outfile.write("CPU Disk,")
#			config.temp_log_outfile.write(",")
#			config.temp_log_outfile.write(",")
			config.temp_log_outfile.write("\n")
		logtime = datetime.now()
		logtime_text = (str(logtime.day).zfill(2) + "/" + str(logtime.month).zfill(2) + 
			"/" + str(logtime.year).zfill(2) + " " + str(logtime.hour).zfill(2) + ":" + 
			str(logtime.minute).zfill(2) + ":" + str(logtime.second).zfill(2))
		config.temp_log_outfile.write(logtime_text + ",")
		for z in range(0,len(cpu_bffr_values),1):
			config.temp_log_outfile.write(str(cpu_bffr_values[z]) + ",")
		config.temp_log_outfile.write("\n")
		config.temp_log_outfile.flush()
		
		return
		
	def send_log_by_ftp(self,FTP_dbug_flag,remote_log_dir):
		here = "my_sensors.send_log_by_ftp"
		ftp_result = send_by_ftp(FTP_dbug_flag,self.__ftp_creds, self.__temp_log_filename_save_as, \
			self.__temp_log_filename,remote_log_dir)
		for pres_ind in range(0,len(ftp_result)):
			pr(FTP_dbug_flag,here, str(pres_ind) + " : ", ftp_result[pres_ind])
		if self.__send_plain_count < 0 :
			ftp_result = send_by_ftp(FTP_dbug_flag,self.__ftp_creds, self.__temp_log_filename_save_as, \
				"temp_log.csv",remote_log_dir)
			for pres_ind in range(0,len(ftp_result)):
				pr(FTP_dbug_flag,here, str(pres_ind) + " : ", ftp_result[pres_ind])
			self.__send_plain_count = 10
		else:
			self.__send_plain_count -= 1
		return
					
	def copy_log_to_www(self,dbug_flag):
		here = "copy_log_to_www"
		try:
			# send the same html file to the local web site
			copyfile(self.__temp_log_filename_save_as, self.__local_www_temp_log_filename)
			pr(dbug_flag,0, "Sent : " + self.__temp_log_filename_save_as + " to : ", self.__local_www_temp_log_filename)
		except:
			pr(True,0,"Fail with copy " + self.__temp_log_filename_save_as + " to : ", self.__local_www_temp_log_filename)


