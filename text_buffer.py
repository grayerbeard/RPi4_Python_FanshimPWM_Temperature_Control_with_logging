#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	text_buffer
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
from datetime import datetime
from shutil import copyfile
from sys import exit as sys_exit
import os

# Third party imports
# None

# Local application imports
from utility import pr,make_time_text,send_by_ftp
from buffer_log import class_buffer_log

class class_text_buffer(object):
	# Rotating Buffer Class
	# Initiate with just the size required Parameter
	# Get data with just a position in buffer Parameter
	def __init__(self, size_max, headings,name,config,log_buffer_flag):
		#initialization
		print(" Buffer Init for : ",name," with a size of : ",size_max, " and  width of : ", len(headings) + 1, " including time stamp")
		if not os.path.exists('log'):
		    os.makedirs('log')
		self.__source_ref = 0 # a number used to control prevention repeat messages
		self.__size_max = size_max
		self.__name = name # used for debugging which bugger instance in use
		self.__width = len(headings) + 1                     
		self.line_values = ["1"]*len(headings)
		self.__dta = [ [ None for di in range(self.__width+1) ] for dj in range(self.__size_max+1) ]
		self.__size = 0
		self.__posn = self.__size_max-1
		# self.__html_filename = "not set"
		# self.__www_filename = "not set"
		# self.__ftp_creds = "not set"
		self.__headings = ["Time"]
		for hdg_ind in range(0,self.__width-1):
			#print(hdg_ind,headings[hdg_ind])
			self.__headings.append(headings[hdg_ind])
		#print(self.__headings)
		self.__pr_values = ["text"] * self.__width
		self.__config = config
		self.__html_filename = name + "_log.html"
		self.__html_filename_save_as = config.prog_path + self.__html_filename
		self.__www_filename = config.local_dir_www +  self.__html_filename  
		self.__ftp_creds = config.ftp_creds_filename
		if log_buffer_flag:
			self.__log_buffer_flag = True
			self.__send_log_count = 0
			self.__log = class_buffer_log(name,config)
		else:
			self.__log_buffer_flag = False

		
	def size(self):
		return self.__size_max

	def update_buffer(self,values,appnd,ref):
		#append a line of info at the current position plus 1 
		# print("Update Buffer appnd and ref are : ",appnd,ref)
		if appnd + (self.__source_ref != ref):
			#we adding message and incrementing posn
			if self.__size < self.__size_max-1 :
				self.__size += 1
			if self.__posn == self.__size_max-1:
				# last insert was at the end so go back to beginning@@
				self.__posn = 0
			else:
				# first increment insert position by one
				self.__posn += 1
				# then insert a line full of values
			self.__source_ref = ref
		else:
			self.__source_ref = ref		
		if len(values) > self.__width :
			print("Width Error for :",self.__name, len(values) , self.__width, values)
			sys.exit()
		for i in range(0,len(values)):
			self.__dta[self.__posn][i] = values[i]

		#print("Buffer updated and log buffer flag is : ",self.__log_buffer_flag)
		if self.__log_buffer_flag:
			self.__log.log_to_file(self.__headings,values)
			self.__log.copy_log_to_www(False)
			#send log file to website configevery ten scans
			if self.__send_log_count > 10:
				#print("Sending log file by FTP")
				self.__log.send_log_by_ftp(False,self.__config.log_directory,self.__config.ftp_timeout)
				self.__send_log_count = 0
			else:
				#print("not FTP This Time count is : ",self.__send_log_count)
				self.__send_log_count += 1

 
	def get_line_dta(self, key):
		#return stored element from position relative to current insert position in buffer
		line_dta = [" - "]*self.__width 		
		if (self.__posn-key) > -1:
			# need to take values from arlogea before current insert position
			for i in range(self.__width):
				line_dta[i] = self.__dta[self.__posn-key][i]
			return(line_dta)
		else:
			# need to take values from after current insert position
			for i in range(self.__width):
				#following two lines used too debug the calc to get the lower part of status file
				#print("That Calc key,self.__size,self.__size_max, self.__posn-key,key sum",
				 #  key,self.__size,self.__size_max, self.__posn-key,(self.__posn-key),self.(size_max + (self.__posn-key))
				line_dta[i] = self.__dta[self.__size_max + (self.__posn-key)][i]
			return(line_dta)	

	def get_dta(self):
		# get all the data inserted so far, or the whole buffer
		all_data = [ [ None for di in range(self.__width+1) ] for dj in range(self.__size_max+1) ]
		for ind in range(0,self.__size):
			line_dta = self.get_line_dta(ind)
			# Following line for debug data from Buffer
			# print("get_dta >>>",ind,line_dta)
			for i in range(len(line_dta)):    
				all_data[ind][i] = line_dta[i]
		return(all_data)

	def pr(self,appnd,ref,log_time,refresh_interval):
		here = "buffer.pr for " + self.__name
		make_values = [" -- "]*self.__width
		prtime = datetime.now()
		for_screen = log_time.strftime('%d/%m/%Y %H:%M:%S')
		# following alternative will show more resolution for fractions of a second
		# for_screen = log_time.strftime('%d/%m/%Y %H:%M:%S.%f')      
		make_values[0] = for_screen
		file_start = """<head>
<meta http-equiv="refresh" content="""
		file_start = file_start + str(refresh_interval)
		file_start = file_start + """ />
</head>
<caption>Rotating Buffer Display</caption>"""
		tbl_start = """ <p>
<table style="float: left;" border="1">
<tbody>"""
		tbl_start_line = """<tr>"""
		tbl_end_line = """</tr>"""
		tbl_start_col = """<td>"""
		tbl_end_col= """</td>"""
		tbl_end = """</tbody>
</table>"""
		file_end = """
</body>
</html>"""
		try:
			for i in range(0,self.__width -1):
				make_values[i+1] = str(self.line_values[i])
				for_screen = for_screen + " " + str(self.line_values[i])
		except:
			print("Error in make values in ...buffer.pr for : ",self.__name)
			print("i,values,len(self.line_value>s),self.__width",i,self.line_values,len(self.line_values),self.__width)
			sys_exit()
				
		# print to screen and to status log and update html file
		
		if appnd:
			print("    appending : " + self.__name + " : " + for_screen)
		else:
			print("not appending : " + self.__name + " : " + for_screen)

		self.update_buffer(make_values,appnd,ref)
		with open(self.__html_filename,'w') as htmlfile:
			htmlfile.write(file_start)
			htmlfile.write("<p>" + self.__html_filename + " : " + make_time_text(datetime.now())  + "</p>\n<p>")
			htmlfile.write(tbl_start + tbl_start_line)
			for ind in range(0,len(self.__headings)):
				htmlfile.write(tbl_start_col + self.__headings[ind] + tbl_end_col)
			htmlfile.write(tbl_end_line)
			buffer_dta = self.get_dta()
			for ind in range(self.__size):
				htmlfile.write(tbl_start_line)
				for i in range(self.__width):
					htmlfile.write(tbl_start_col + str(buffer_dta[ind][i]) + tbl_end_col)
				htmlfile.write(tbl_end_line)
			htmlfile.write(tbl_end)
			htmlfile.write(file_end)
		copyfile(self.__html_filename, self.__www_filename)
		
		# To debug FTP change end of following line to " = True"
		
		FTP_dbug_flag = True
		print("############ sending by FTP dbug on")
		
		ftp_result = send_by_ftp(FTP_dbug_flag,self.__ftp_creds, self.__html_filename_save_as, self.__html_filename,"",self.__config.ftp_timeout)
		for pres_ind in range(0,len(ftp_result)):
			pr(FTP_dbug_flag,here, str(pres_ind) + " : ", ftp_result[pres_ind])
		return






