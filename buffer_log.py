#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	buffer_log.py
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

# Third party importstemp_log
# none
 
# Local application imports
from utility import pr,make_time_text,send_by_ftp

class class_buffer_log:
	def __init__(self,config):
		self.dbug = False
		self.__send_plain_count = 5
		self.__no_heading_yet = True
		self.__config = config
		starttime = datetime.now()
		timestamp = make_time_text(starttime)
		self.__log_filename = timestamp + "_" + self.__config.prog_name + "_" + "lg.csv"
		print(self.__config.prog_path,self.__config.log_directory)
		self.__log_filename_save_as = self.__config.prog_path + self.__config.log_directory + self.__log_filename
		self.__local_www_log_filename = self.__config.local_dir_www + self.__config.log_directory + self.__log_filename


	def log_to_file(self,log_headings,log_values):
		here = 	"log_cpu_data_to_file"
		#write the time at the start of the line in logging file
	
		if self.__no_heading_yet:
			self.__no_heading_yet = False
			self.__log_file = open(self.__log_filename_save_as,'w')
			for hdg_ind in range(0,len(log_headings)):
				self.__log_file.write(log_headings[hdg_ind] + ",")
			self.__log_file.write("\n")
		for z in range(0,len(log_values),1):
			self.__log_file.write(str(log_values[z]) + ",")
		self.__log_file.write("\n")
		self.__log_file.flush()
		
		return
		
	def send_log_by_ftp(self,FTP_dbug_flag,remote_log_dir,ftp_timeout):
		here = "bffr_log_log_by_ftp"
		ftp_result = send_by_ftp(FTP_dbug_flag,self.__config.ftp_creds_filename, self.__log_filename_save_as, \
			self.__log_filename,remote_log_dir,ftp_timeout)
		for pres_ind in range(0,len(ftp_result)):
			pr(FTP_dbug_flag,here, str(pres_ind) + " : ", ftp_result[pres_ind])
		if self.__send_plain_count < 0 :
			ftp_result = send_by_ftp(FTP_dbug_flag,self.__config.ftp_creds_filename, self.__log_filename_save_as, \
				"log.csv",remote_log_dir,ftp_timeout)
			for pres_ind in range(0,len(ftp_result)):
				pr(FTP_dbug_flag,here, str(pres_ind) + " : ", ftp_result[pres_ind])
			self.__send_plain_count = 10
		else:
			self.__send_plain_count -= 1
			#print("Send plain count : ",self.__send_plain_count)
		return
					
	def copy_log_to_www(self,dbug_flag):
		here = "copy_log_to_www"
		try:
			# send the same html file to the local web site
			copyfile(self.__log_filename_save_as, self.__local_www_log_filename)
			pr(dbug_flag,0, "Sent : " + self.__log_filename_save_as + " to : ", self.__local_www_log_filename)
		except:
			pr(True,0,"Fail with copy " + self.__log_filename_save_as + " to : ", self.__local_www_log_filename)


