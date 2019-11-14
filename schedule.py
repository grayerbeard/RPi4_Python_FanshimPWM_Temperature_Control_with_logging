#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	schedule.py
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

class class_my_sensors:
	def __init__(self,max_width):
		self.__s_filename = "sensor_data.csv" # the default file name
		self.__html_filename_save_as = "not_set"
		self.__html_filename = "not_set"
		self.__www_filename = "not_set"
		self.__ftp_creds =  "not_set"
		self.max_width = max_width # maximum width for data array usually 5
		self.width = 0 # number of sensors we have data for so far
		
		self.sensor_present = False
		self.dbug = False
		self.number_seen = 0
		self.sensor4readings = "not_set"
		self.ref_sensor_index =-1
		
		self.number = [0]*self.max_width		# number designation of sensor to use for display
		self.code = ["-"]*self.max_width			# the code that the sensor is internally programmed with
		self.connected = [False]*self.max_width		# true/false flag indicating if his sensor is connected obtained by scanning for its file
		self.reading = [-100]*self.max_width		# the last temperature reading read from the sensor in degrees Centigrade, 
								# will be a negative value < -100 if there is an error in reading
		self.last_logged = [-100]*self.max_width	# the value last logged for that sensor
		self.code_seen = [False]*self.max_width		# a true/false flag indicating that this senso code has been seen during this run
		self.code_seen_but_disconnected = [False]*self.max_width	# Flag for when we have seen a sensor then its disconnected
		self.location = [" - "]*self.max_width		# text read in from the sensor data file for the sensors location
		self.stype = [" - "]*self.max_width			# text read in from the sensor data file for the sensors type
		self.comment = [" - "]*self.max_width		# text read in from the sensor data file for a comment
		self.delay = [0]*self.max_width			# if the sensor is not responding, maybe has become disconnected
		self.error_number = [-1]*self.max_width	# then its file will still be present for a while and this number is
		self.last_logged_error_number = [-1]*self.max_width # Last logged error
		self.status_text = [0]*self.max_width	# used to count down before retrying, initially set to the observed delay
								# then 0.5 subtracted each scan until value less than 0.5.
								# delay is usually around 2 secosnds so it will be about 3 scans before another attempt is made.
		self.__s_filename =  "not set"
		self.__log_filename =  "not set"
		self.__log_filename_save_as = "not_set"
		self.__html_filename =  "not set"
		self.__www_filename =  "not set"
		self.__www_log_filename =  "not set"
		self.__ftp_creds =  "not set"
		self.__log_count = 0
		
		self.__status_html_filename = "not set"
		self.__log_html_filename = "not set"		

	def set_s_filename(self,s_filename):
		# csv file that holds the sensor data
		print ( "setting s_filename to :" , s_filename )
		self.__s_filename =  s_filename
		
	def set_log_filename(self,log_filename):
		# local file for logging to
		self.__log_filename = log_filename
		
	def set_log_filename_save_as(self,log_filename_save_as):
		# local file for logging to
		self.__log_filename_save_as = log_filename_save_as
		
	def	set_log_html_filename(self,log_html_filename):
		# html logging file
		self.__log_html_filename = log_html_filename
		
	def	set_status_html_filename(self,status_html_filename):
		# html logging file
		self.__status_html_filename = status_html_filename
		
	def set_local_html_filename_save_as(self, html_filename_save_as):
		# local html file for sending to web sites
		self.__html_filename_save_as = html_filename_save_as
		
	def set_local_html_filename(self, html_filename):
		# local html file for sending to web sites
		self.__html_filename = html_filename

	def set_www_filename(self,www_filename):
		# local website html file
		self.__www_filename = www_filename
		
	def set_www_log_filename(self,www_log_filename):
		# local website filename for loggingf filer
		self.__www_log_filename = www_log_filename

	def set_ftp_creds(self,ftp_creds):
		# creds file used to send logging file 
		self.__ftp_creds = ftp_creds
		
	def set_sensor4readings(self,sensor4readings):
		# creds file used to send logging file 
		self.sensor4readings = sensor4readings

	def read_file(self):
		#	Set sensor data lists with initial values
		#	read in from file if it exists if not then set up
		#	just defaults for one sensor
		#	later any sensors that are connected will be added
		#global my_sensors
		#global smartplug_info
		#global config
		here = "mysensors.read_file"
		#pr(here, "dictionary of my_sensors : ", self.__dict__ )
		with open(self.__s_filename, 'r') as csvfile:
			d_file = csv_DictReader(csvfile)
			self.width = 0
			ind = 0
			for row in d_file:
				self.number[ind] = row['number']
				self.code[ind] = row['code']
				self.connected[ind] = False
				self.reading[ind] = -108
				self.last_logged[ind] = -108
				self.code_seen[ind] = False
				self.code_seen_but_disconnected[ind] = False
				self.location[ind] = row['location']
				self.stype[ind] = row['stype']
				self.comment[ind] = row['comment']
				self.delay[ind] = 0
				self.error_number[ind] = 2
				self.last_logged_error_number[ind] = 2
				self.status_text[ind] = "?"
				self.width += 1
				ind += 1
				if ind > self.max_width:
					print("Two many items in file for max width of : ", self.max_width)
					break
		return(True)

	def write_file(self,new_data_count,new_file):
		# add a new record to the sensor file
		#global my_sensors
		#global config
		#global smartplug_info
	
		here = "mysensors.write_file"
		pr(self.dbug,here, "write_sensor_data will write : ", new_data_count)
		fields = ['number','code','location','stype','comment']
		# 'at' mode adds toimport sys, getopt end of the file and opens file as text
		if new_file:
			mode = 'wb'
		else:
			mode = 'at'
		if self.__s_filename == "":
			pr(True,here,"No Sensor File Name set", 1.234)
			sys_exit()
		try:
			with open(self.__s_filename, mode) as sensorcsv_file:
				writer = csv_DictWriter(sensorcsv_file, fieldnames = fields)
				if new_file: # this is a blank file
					writer.writeheader() # new file needs headings.
				for line_count in  range(self.width-new_data_count,self.width,1):
					writer.writerow({
					'number': self.number[line_count],
					'code': self.code[line_count],
					'location': self.location[line_count],
					'stype': self.stype[line_count],
					'comment': self.comment[line_count]
					})
		except:
			pr(True,here,"Error accessing the existing sensor info file", self.__s_filename)
			pr(True,here,"Try deleting file let prog make a new one", self.__s_filename)
			sys_exit()
		return

	def get_temps(self):
		# check which sensors are connected and update relavant flags
		# build a list of all the new sensors and then add them to the data in use
		# note :  requires that my_sensors variable is populated
		#global my_sensors
		#global smartplug_info
		#global config
		here = "get_temps"
		# Look for what sensors are connected 	
		sensors = W1ThermSensor.get_available_sensors()
		connected_codes = ["nocodeyet"]*len(sensors)
		connected_temp = [-100]*len(sensors)
		
		pr(self.dbug,here, " number seen", len(sensors) )
		
		ind = 0
		
		for individual_sensor in W1ThermSensor.get_available_sensors():
			#follwoing does not work so commented out
			#try:
				#individual_sensor.set_precision(config.precision)
			#except:
			#	pr(self.dbug,here, "Cannot Change Precision" , str(individual_sensor.id) ) 
			connected_codes[ind] =  individual_sensor.id
			try:
				connected_temp[ind] = individual_sensor.get_temperature()
			except:
				pr(self.dbug,here, "Error Reading scanned item", str(ind)  + " : " + individual_sensor.id)
				connected_temp[ind] = -100
			pr(self.dbug,here   ,  "Scan of seen sensors" ,   str(ind) + " : " + connected_codes[ind] + " : " + str(connected_temp[ind]))
			ind += 1
		
		self.number_seen = ind
		
		if len(sensors) > 0:
			self.sensor_present = True
			pr(self.dbug,here, "Sensor present Set True with count equal to : ", str(len(connected_codes)))
		else:
			pr(self.dbug,here, "Sensor present not Set with count equal to : ", str(len(connected_codes)))
			self.sensor_present = False
		
		new_codes = []
		self.ref_sensor_index = -1
		for my_sensor_count in range(0,len(self.code)):
			self.code_seen[my_sensor_count] = False
			self.reading[my_sensor_count] = -100 # signal that no data seen
			self.error_number[my_sensor_count] += 1
			for seen_count in range (0,self.number_seen):
				if connected_codes[seen_count] == self.code[my_sensor_count]:
					# set flag to indicate has been seen during this run of program
					pr(self.dbug,here, "Scanning My Count, seen count ", str(my_sensor_count) + " :" + str(seen_count) + " : " +  str(connected_temp[seen_count]) )
					self.code_seen[my_sensor_count] = True
					self.connected[my_sensor_count] = True
					self.error_number[my_sensor_count] = 0  # signal that its not in error
					if connected_temp[seen_count] != -100:
						# codeget_temps there but not ready to be read
						self.reading[my_sensor_count] = connected_temp[seen_count] # copy across id temp found
					else:
						self.reading[my_sensor_count] = -100
						self.code_seen[my_sensor_count] = False
						self.error_number[my_sensor_count] = 1
					if self.code[my_sensor_count] == self.sensor4readings:
						self.ref_sensor_index = my_sensor_count
					self.code_seen_but_disconnected[my_sensor_count] = False
		count_connected = 0
		new_codes = []
		for element in connected_codes:
			if not element in self.code:
				new_codes.append(element)
			count_connected  += 1
		if len(new_codes) > 0:
			pr(self.dbug,here, str(len(new_codes)), " new sensors found")
			new_ind = 0 # index for new_codes
			start_entering_data = self.width
			end_at = self.width + len(new_codes)
			self.width = end_at # the number sensors whose data stored and pointer where put next
			for ind in range(start_entering_data, end_at):
				if ind > self.max_width:
					print("Too Many sensors, new ones not added")
					break
				#if len(self.number) > 0:
				#	self.number.append("n" + str(count_connected-len(new_codes)+ind+1))
				#else:
				#	self.number.append("n" + str(1))
				
				print("for debug;   ind : ",ind)
				
				
				
				self.number[ind] = "nxx"
				self.code[ind] = new_codes[new_ind]
				self.connected[ind] = True
				self.reading[ind] = -102
				self.last_logged[ind] = -102
				self.code_seen[ind] = True
				self.code_seen_but_disconnected[ind] = False
				self.location[ind] = "Lxx"
				self.stype[ind] ="Txx"
				self.comment[ind] ="Ccc"
				self.delay[ind] = 0
				self.error_number[ind] = 2
				self.status_text[ind] = "New"
				self.last_logged_error_number[ind] = 2
				new_ind += 1
		else:
			pr(self.dbug,here, "no new codes, still only : ", str(count_connected) + " connected")
		return(len(new_codes))
		
	def send_html_by_ftp(self,config,smartplug_info,target_temp,target_full_power):
		here = "sensors.send_by_ftp"

		ftp_text_linestart = "<tr align=\"center\" valign=\"middle\"><td>"
		ftp_text_line_end = "</td></tr>"
		ftp_text_end = ["</tbody>"]
		ftp_text_between = "</td><td>"
		ftp_start = """<!--
Temperature Logging and Control
-->
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
"http://www.w3.oset_log_html_filenamerg/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<title>Temperature Logging and Control</title>
<meta http-equiv="content-type" content="text/html;charset=utf-8" />
<meta http-equiv="refresh" content="15" />
</head>
<body><table style="background-color: #f4e7e7; width: 350px; height: 150px; border: 1px solid #1b58e4;\" cellpadding=\"5\" align=\"center\">
<caption>Temperatures Logging</caption><tbody>"""
		ftp_end = """</td></tr>
</table>")
</body>
</html>"""

		if self.__html_filename == "not_set":
			pr(self.dbug,here,"Error", "html filename not set")
		if self.__www_filename ==  "not_set":
			pr(self.dbug,here,"Error", "html filename not set")
		if self.__ftp_creds ==  "not_set":
			pr(self.dbug,here,"Error", "html filename not set")

		with open(self.__html_filename,'w') as htmlfile:
			htmlfile.write(ftp_start)
			htmlfile.write(ftp_text_linestart + " Scan Count:  " + ftp_text_between  \
											+ str(config.scan_count) + ftp_text_line_end)	  
			htmlfile.write(ftp_text_linestart + "  System Time: " + ftp_text_between  \
											+ make_time_text(datetime.now()) + ftp_text_line_end)
			htmlfile.write(ftp_text_linestart + " Html Log File: " + ftp_text_between \
											+ "<a href=\"" + self.__log_html_filename + "\" target = \"_blank\">" \
											+ self.__log_html_filename + "</a>" + ftp_text_line_end)
			htmlfile.write(ftp_text_linestart + " Status File: " + ftp_text_between +  "<a href=\"" + \
				str(self.__status_html_filename) +  "\" target = \"_blank\">"  + \
				str(self.__status_html_filename) + "</a>"  + ftp_text_line_end)
			htmlfile.write(ftp_text_linestart + " Debug File: " + ftp_text_between +  "<a href=\"" + \
				str("debug.html") +  "\" target = \"_blank\">"  + \
				str("debug.html") + "</a>"  + ftp_text_line_end)
			htmlfile.write(ftp_text_linestart + " WD Log File: " + ftp_text_between +  "<a href=\"" + \
				str("wd_log.html") +  "\" target = \"_blank\">"  + \
				str("wd_log.html") + "</a>"  + ftp_text_line_end)
			htmlfile.write(ftp_text_linestart + " CSV Log File: " + ftp_text_between  + "<a href=" + "\"" + str(self.__log_filename_save_as) + "\"" + "target = \"_blank\">"  + str(self.__log_filename) + "</a>"  + ftp_text_line_end)
			s_numb = 0
			for element in self.number:
				htmlfile.write(ftp_text_linestart + str(element) + ftp_text_between + str(self.location[s_numb]) + \
					ftp_text_between + str(self.status_text[s_numb]) + ftp_text_line_end)
				s_numb +=1
			if config.sauna:
				htmlfile.write(ftp_text_linestart + "Sauna" + ftp_text_between + "Target/Offset/On" + \
					ftp_text_between + "{0:.4}/{1:.4}/{2:.4}".format( \
					float(config.default_target),float(config.target_offset),float(config.percent_full_power * config.sauna_on)) + \
					ftp_text_line_end)
			else:	
				htmlfile.write(ftp_text_linestart + "Plug 1 Power and Total" + ftp_text_between + str(smartplug_info.power[0]) + ftp_text_between + str(smartplug_info.total[0]) + ftp_text_line_end)
				htmlfile.write(ftp_text_linestart + "Plug 2 Power and Total"+ ftp_text_between + str(smartplug_info.power[1]) + ftp_text_between + str(smartplug_info.total[1]) + ftp_text_line_end)
				htmlfile.write(ftp_text_linestart + "Scheduled" + ftp_text_between + "Target Temp : " + ftp_text_between + str(target_temp) + ftp_text_line_end)
				htmlfile.write(ftp_text_linestart + "Scheduled" + ftp_text_between + "Target Full Power : " + ftp_text_between + str(target_full_power) + ftp_text_line_end)
			for element in ftp_text_end:
				htmlfile.write(element)
		# Change "False" to "True" on next line to debug FTP
		FTP_dbug_flag = False
		ftp_result = send_by_ftp(FTP_dbug_flag,self.__ftp_creds, self.__html_filename, "index.html","")
		for pres_ind in range(0,len(ftp_result)):
			pr(FTP_dbug_flag,here, str(pres_ind) + " : ", ftp_result[pres_ind])
		
		try:
			# send the same html file to the local web site
			copyfile(self.__html_filename, self.__www_filename)
			pr(self.dbug,0, "Sent : " + config.html_filename + " to : ", config.local_www_html_filename)
		except:
			pr(self.dbug,0,"Fail with copy " + config.html_filename + " to : ", config.local_www_html_filename)


	def set_status_text(self,config):
		# set the status text based on the results of the last scan
		self.status_text_error_count = 0
		here = "mysensors.set_status_text"
		for z in range(0,len(self.code),1):
			pr(self.dbug,here, "setting status text (index:error:reading) ", str(z) + " : " + str(self.error_number[z]) + " : " +  str(self.reading[z]))
			if self.error_number[z] == 0 :
				self.status_text[z] = ("{0:.4}".format(float(self.reading[z])))
			else:
				self.status_text_error_count +=1
				if self.delay[z] >= config.delay_limit:
					self.status_text[z] = ("Wait : " + str(int(self.delay[z])))
				else:
					self.status_text[z] = ("Err# : " + str(self.error_number[z]))

	def make_printout_for_screen(self,target_temp,ref_temp,config,smartplug_info):
		here = "make_printout_for_screen"
		# self.print_out_error_count = 0
		#set printout for start of the line

		printout = [str(config.scan_count)]

		if config.sauna:
			printout.append("{0:.4}".format(float(target_temp)))
			printout.append("{0:.4}".format(float(ref_temp)))
			printout.append("{0:.4}".format(float(config.percent_full_power * config.sauna_on)))
			printout.append("{0:.4}".format(float(config.target_offset)))
			printout.append("{0:.4}".format(float(config.detect_off_count)))
		else:
			printout.append("{0:.4}".format(float(target_temp)))
			printout.append("{0:.4}".format(float(ref_temp)))
			for z in range(0,self.max_width,1):
				printout.append(self.status_text[z])
			printout.append(str(smartplug_info.current[0]))
			printout.append(str(smartplug_info.voltage[0]))
			printout.append(str(smartplug_info.power[0]))
			printout.append(str(smartplug_info.total[0]))
			printout.append(str(smartplug_info.current[1]))
			printout.append(str(smartplug_info.voltage[1]))
			printout.append(str(smartplug_info.power[1]))
			printout.append(str(smartplug_info.total[1]))
		return(printout)

	def log_to_file(self,config, smartplug_info,target_temp,ref_sensor,dbug_flag,smart_log_width):
		here = 	"log_temperature_data_to_file"
		#write the time at the start of the line in logging file
		
		if self.__log_count == 0 : 
			config.logging_outfile.write("Time,")
			config.logging_outfile.write("Count,")
			config.logging_outfile.write("Target,")
			config.logging_outfile.write("Ref Sensor,")
			if config.sauna:
				config.logging_outfile.write("On,")
				config.logging_outfile.write("Offset,")
				config.logging_outfile.write("Detect Off")
				config.logging_outfile.write("\n")
			else:
				for hdg_ind in range(1,(self.max_width+1)):
					config.logging_outfile.write("T" + str(hdg_ind)+",")
				config.logging_outfile.write("I1,")
				config.logging_outfile.write("V1,")
				config.logging_outfile.write("P1,")
				config.logging_outfile.write("T1,")
				config.logging_outfile.write("I2,")
				config.logging_outfile.write("V2,")
				config.logging_outfile.write("P2,")
				config.logging_outfile.write("T2,")
				config.logging_outfile.write("\n")
		self.__log_count += 1
		logtime = datetime.now()
		logtime_text = (str(logtime.day).zfill(2) + "/" + str(logtime.month).zfill(2) + 
			"/" + str(logtime.year).zfill(2) + " " + str(logtime.hour).zfill(2) + ":" + 
			str(logtime.minute).zfill(2) + ":" + str(logtime.second).zfill(2))
		config.logging_outfile.write(logtime_text)
		if (self.sensor_present == False):
			config.logging_outfile.write(" : no sensors with Trg Temp of : " + str(target_temp) + "\n")
		else:
			config.logging_outfile.write("," + str(self.__log_count) + ",")
			config.logging_outfile.write(str(target_temp) + ",")
			config.logging_outfile.write(str(ref_sensor) + ",")
			if config.sauna:
				config.logging_outfile.write(str(config.percent_full_power * config.sauna_on)+ ",")
				config.logging_outfile.write(str(config.target_offset) + ",")
				config.logging_outfile.write(str(config.detect_off_count))
			else:
				for z in range(0,self.max_width,1):
					#record the data last saved for this sensor
					#send data to the file only if the sensor is connected
					config.logging_outfile.write(str(self.status_text[z]) + ",")
					self.last_logged[z] = self.reading[z]
					self.last_logged_error_number[z] = self.error_number[z]
				config.logging_outfile.write(str(smartplug_info.current[0]))
				config.logging_outfile.write("," + str(smartplug_info.voltage[0]))
				config.logging_outfile.write("," + str(smartplug_info.power[0]))
				config.logging_outfile.write("," + str(smartplug_info.total[0]))
				pr(dbug_flag,here,"Total power going to log file", smartplug_info.total[0])
				#config.logging_outfile.write("," + str(smartplug_info.error[1]))
				#config.logging_outfile.write("," + str(smartplug_info.state[1]))
				config.logging_outfile.write("," + str(smartplug_info.current[1]))
				config.logging_outfile.write("," + str(smartplug_info.voltage[1]))
				config.logging_outfile.write("," + str(smartplug_info.power[1]))
				config.logging_outfile.write("," + str(smartplug_info.total[1]))
				pr(dbug_flag,here,"Total power going to log file", smartplug_info.total[1])
				#config.logging_outfile.write("," + str(smartplug_info.error[1]))
			config.logging_outfile.write("\n")
			config.logging_outfile.flush()
		return
		
	def send_log_by_ftp(self,FTP_dbug_flag,remote_log_dir):
		here = "my_sensors.send_log_by_ftp"
		ftp_result = send_by_ftp(FTP_dbug_flag,self.__ftp_creds, self.__log_filename_save_as, \
			self.__log_filename,remote_log_dir)
		# Folowing useful to debug the remote directory
		# pr(FTP_dbug_flag,here,"### FTP_dbug_flag,self.__ftp_creds, self.__log_filename_save_as, self.__log_filename,remote_log_dir", \
		#	str(FTP_dbug_flag) + ":" + str(self.__ftp_creds) + ":" + str(self.__log_filename_save_as) + \
		#	":" + str(self.__log_filename) + ":" + str(remote_log_dir))
		for pres_ind in range(0,len(ftp_result)):
			pr(FTP_dbug_flag,here, str(pres_ind) + " : ", ftp_result[pres_ind])
		return
			
	def copy_log_to_www(self,dbug_flag):
		here = "copy_log_to_www"
		try:
			# send the same html file to the local web site
			copyfile(self.__log_filename_save_as, self.__www_log_filename)
			pr(dbug_flag,0, "Sent : " + self.__log_filename_save_as + " to : ", self.__www_log_filename)
		except:
			pr(True,0,"Fail with copy " + self.__log_filename_save_as + " to : ", self.__www_log_filename)

class old_class_schedule:
	def __init__(self):
		self.index = []		# Index of the array holding the Temperature Schedule
		self.year = []		# Year
		self.month = []		# Month
		self.day = []		# Day
		self.hour = []		# Hour
		self.minute = []		# Minute
		self.target_temp = []	# Target Temperature

	def old_read_in_schedule_data(self,sch_filename):
		#	Read in Schedule data from schedule.csv
		here = "read_in_schedule_data"
		#pr(True,here, "Schedule Data read in : ", self.__dict__ )
		with open(sch_filename) as csvfile:
			d_file = csv_DictReader(csvfile)
			ind = 0
			for row in d_file:
				self.index.append(row['index'])
				self.year.append(row['year'])
				self.month.append(row['month'])
				self.day.append(row['day'])
				self.hour.append(row['hour'])
				self.minute.append(row['minute'])
				self.target_temp.append(row['target_temp'])
			ind += 1
		return(True)

	def old_get_target_temp(self,time_now,config):

		# From Schedule get Target Temperature
				
		target_temp = class_temp_values()
		
		# Search for Target Temp
		for ind in range(1,len(self.year)):
			if int(time_now.year) == int(self.year[ind]):
				if int(time_now.month) == int(self.month[ind]):
					if int(time_now.day) == int(self.day[ind]):
						if int(time_now.hour) == int(self.hour[ind]):
							if int(time_now.minute) >= int(self.minute[ind]):
								if int(time_now.minute) <= int(self.minute[ind+1]):
									target_temp.ind_result = ind
									break
								else:
									target_temp.ind_result = ind	
				
		if target_temp.ind_result == 1:
			target_temp.status = True
			target_temp.text = "Before Schedule Start"
			target_temp.value = config.default_target - 0.1
			pr(True,0,"Error or very new schedule >> ind result : "  + str(target_temp.ind_result) +  "Target set to", target_temp.value)
			return (target_temp)
		else:
			if target_temp.ind_result +1 > len(self.year):
				target_temp.status = True
				target_temp.text = "After Schedule End"
				target_temp.value = config.default_target - 0.2
				pr(True,0,"Error>> ind result : " + target_temp.ind_result +  "Target set to", target_temp.value)
				return (target_temp)
			else:
				pr(config.dbug,0,"Schedule Look Up Result>> index used: ", str(target_temp.ind_result+1).zfill(4) + "  Date : "
				+ str(self.year[target_temp.ind_result+1]).zfill(4) + "/" + str(self.month[target_temp.ind_result+1]).zfill(2) + "/"
				 + str(self.day[target_temp.ind_result+1]).zfill(2) +" Time: " + str(self.hour[target_temp.ind_result+1]).zfill(2) +":" 
				 + str(self.minute[target_temp.ind_result+1]).zfill(2) +" Target : " + str(self.target_temp[target_temp.ind_result+1]))
				# following is a dodge to deal with errors in the file 
				try:
					if (config.default_target / 10) <= float(self.target_temp[target_temp.ind_result+1]) <= (config.default_target * 2):
						target_temp.status = True
						target_temp.text = self.target_temp[target_temp.ind_result+1]
						target_temp.value = float(self.target_temp[target_temp.ind_result+1])
						print("looked up value in range: ", target_temp.value)
						return (target_temp)
					else:
						target_temp.status = False
						target_temp.text = self.target_temp[target_temp.ind_result+1]
						target_temp.value = float(self.target_temp[target_temp.ind_result+1])
						print("File Error", str(target_temp.ind_result+1).zfill(4) + "  Date : "
							+ str(self.year[target_temp.ind_result+1]).zfill(4) + "/" + str(self.month[target_temp.ind_result+1]).zfill(2) + "/"
							+ str(self.day[target_temp.ind_result+1]).zfill(2) +" Time: " + str(self.hour[target_temp.ind_result+1]).zfill(2) +":" 
							+ str(self.minute[target_temp.ind_result+1]).zfill(2) +" Target : " + str(self.target_temp[target_temp.ind_result+1]))	
						return (target_temp)	
				except:
					target_temp.status = False
					target_temp.text = self.target_temp[target_temp.ind_result+1]
					target_temp.value = -100
					print("File Error", str(target_temp.ind_result+1).zfill(4) + "  Date : "
						+ str(self.year[target_temp.ind_result+1]).zfill(4) + "/" + str(self.month[target_temp.ind_result+1]).zfill(2) + "/"
						+ str(self.day[target_temp.ind_result+1]).zfill(2) +" Time: " + str(self.hour[target_temp.ind_result+1]).zfill(2) +":" 
						+ str(self.minute[target_temp.ind_result+1]).zfill(2) +" Target : " + str(self.target_temp[target_temp.ind_result+1]))	
					return (target_temp)

class class_schedule:
	def __init__(self):
		here = "init"
		print(here)
		self.start_time = [] # Room use start time
		self.room_number = [] # Room Number (shed is 1)
		self.pre_heat_time = [] # Lengthy of time room preheated
		self.on_time = [] # Length of time room in use
		self.in_use_temp = [] # Temperature Required while room in use
		self.min_temp = [] # Minimum Temperature when room not in use
		self.pre_heat_temp = [] # Max temperature during preheat of room
		self.target_2nd_after = [] # Min Temperature before 2nd heater on when room occupied
		self.pre_heat_slope_down = [] #  Rate of reducing temperature during Preheat
		self.pre_heat_slope_up = [] # Rate of increase of temp during room warm up
		self.start_sloping_up_time = [] # Calculated Time when target temp starts to increase for warm up
		self.reach_preheat_time = [] # Calculated Time before Occupation time when room at max preheat
		self.session_end_time = [] # Calculated time when Rooom Occupancy ends
		self.target_temp = -100
		self.target_full_power = -10
		self.error_message = "OK"

	def read_in_schedule_data(self,sch_filename):
		#	Read in Schedule data from schedule.csv
		here = "read_in_schedule_data"
		print(here)
		#pr(True,here, "Schedule Data read in : ", self.__dict__ )
		with open(sch_filename) as csvfile:
			d_file = csv_DictReader(csvfile)
			ind = 0
			for row in d_file:
				self.start_time.append(float(row['start_time'])) # Room use start time
				self.room_number.append(float(row['room_number'])) # Room Number (shed is 1)
				self.pre_heat_time.append(float(row['pre_heat_time'])) # Lengthy of time room preheated
				self.on_time.append(float(row['on_time'])) # Length of time room in use
				self.in_use_temp.append(float(row['in_use_temp'])) # Temperature Required while room in use
				self.min_temp.append(float(row['min_temp'])) # Minimum Temperature when room not in use
				self.pre_heat_temp.append(float(row['pre_heat_temp'])) # Max temperature during preheat of room
				self.target_2nd_after.append(float(row['target_2nd_after'])) # Min Temperature before 2nd heater on when room occupied
				self.pre_heat_slope_down.append(float(row['pre_heat_slope_down'])) #  Rate of reducing temperature during Preheat
				self.pre_heat_slope_up.append(float(row['pre_heat_slope_up'])) # Rate of increase of temp during room warm up
				self.reach_preheat_time.append(self.start_time[ind] - self.pre_heat_time[ind]) # Calculated Time before Occupation time when room at max preheat				
				# print("Calc for reach preheat : ",ind,self.start_time[ind],self.pre_heat_time[ind],self.reach_preheat_time[ind])
				self.start_sloping_up_time.append(self.reach_preheat_time[ind] - ((self.pre_heat_temp[ind] - self.min_temp[ind]) /
					self.pre_heat_slope_up[ind])) # Calculated Time when target temp starts to increase for warm up
				# print ("((self.pre_heat_temp[ind] - self.min_temp[ind]) / self.pre_heat_slope_up[ind])", ((self.pre_heat_temp[ind] - self.min_temp[ind]) / self.pre_heat_slope_up[ind]))
				self.session_end_time.append(self.start_time[ind] + self.on_time[ind]) # Calculated time when Rooom Occupancy ends
				ind += 1
		self.schedule_size = ind - 1
		return(True)

	def all_to_file(self,file_name):
		here = "all_to_file"

		print(here)
		out_file = open(file_name,'w')
		out_file.write("start_time,") # Room use start time
		out_file.write("room_number,")# Room Number (shed is 1)
		out_file.write("pre_heat_time,") # Lengthy of time room preheated
		out_file.write("on_time,") # Length of time room in use
		out_file.write("in_use_temp,") # Temperature Required while room in use
		out_file.write("min_temp,") # Minimum Temperature when room not in use
		out_file.write("pre_heat_temp,") # Max temperature during preheat of room
		out_file.write("target_2nd_after,") # Min Temperature before 2nd heater on when room occupied
		out_file.write("pre_heat_slope_down,") #  Rate of reducing temperature during Preheat
		out_file.write("pre_heat_slope_up,") # Rate of increase of temp during room warm up
		out_file.write("start_sloping_up_time,") # Calculated Time when target temp starts to increase for warm up
		out_file.write("reach_preheat_time,") # Calculated Time before Occupation time when room at max preheat
		out_file.write("session_end_time") # Calculated time when Rooom Occupancy ends
		out_file.write("\n")
		
		for ind in range(0,len(self.start_time)):
			out_file.write(str(self.start_time[ind]) + ",") # Room use start time
			out_file.write(str(self.room_number[ind]) + ",") # Room Number (shed is 1)
			out_file.write(str(self.pre_heat_time[ind]) + ",") # Lengthy of time room preheated
			out_file.write(str(self.on_time[ind]) + ",") # Length of time room in use
			out_file.write(str(self.in_use_temp[ind]) + ",") # Temperature Required while room in use
			out_file.write(str(self.min_temp[ind]) + ",") # Minimum Temperature when room not in use
			out_file.write(str(self.pre_heat_temp[ind]) + ",") # Max temperature during preheat of room
			out_file.write(str(self.target_2nd_after[ind]) + ",") # Min Temperature before 2nd heater on when room occupied
			out_file.write(str(self.pre_heat_slope_down[ind]) + ",") #  Rate of reducing temperature during Preheat
			out_file.write(str(self.pre_heat_slope_up[ind]) + ",") # Rate of increase of temp during room warm up
			out_file.write(str(self.start_sloping_up_time[ind]) + ",") # Calculated Time when target temp starts to increase for warm up
			out_file.write(str(self.reach_preheat_time[ind]) + ",") # Calculated Time before Occupation time when room at max preheat
			out_file.write(str(self.session_end_time[ind])) # Calculated time when Rooom Occupancy ends
			out_file.write("\n")
		out_file.close()


	def get_target_temp(self,now_in_datetime,debug_flag):
		here = "get_target_temp"

		#print(here)
		# Convert to Excel Serial Time Format used by the schedule
		temp = datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
		delta = now_in_datetime - temp
		self.time_now = float(delta.days) + (float(delta.seconds) / 86400)

		self.error_message = "OK"
		found = False
		between = False
		use_minimum = False
		schedule_index = -1
#		debug_signal = 0
		if self.time_now <= self.start_sloping_up_time[0] :
			use_minimum = True
			schedule_index = 0
#			debug_signal = debug_signal + 0.1
		elif self.time_now >= self.session_end_time[len(self.start_time)-1] :
			use_minimum = True
			schedule_index = len(self.start_time) - 1
#			debug_signal = debug_signal + 0.2
		else:
			for ind in range(0,(len(self.start_time)-1)):
				if (self.time_now >= self.start_sloping_up_time[ind]) and (self.time_now <= self.session_end_time[ind]) :
					found = True
					schedule_index = ind
#					debug_signal = debug_signal + 0.3
				elif (self.time_now >= self.session_end_time[ind]) and (self.time_now <= self.start_sloping_up_time[ind +1]) :
					between = True
					schedule_index = ind
#					debug_signal = debug_signal + 0.4
		if debug_flag :
			print("found/between/use_minimum : ",found,between,use_minimum,"schedule_index : ",schedule_index)
		if use_minimum or between:
			self.target_temp = self.min_temp[schedule_index]
			self.target_full_power = self.min_temp[schedule_index]
		elif found :
		# Check for in initial pre heat
			if (self.time_now >= self.start_sloping_up_time[schedule_index]) and (self.time_now <= self.reach_preheat_time[schedule_index]) :
				self.target_temp = self.min_temp[schedule_index] +  (self.pre_heat_slope_up[schedule_index] * \
					(self.time_now - self.start_sloping_up_time[schedule_index]))
				self.target_full_power = self.target_temp
				self.target_full_power = self.target_temp
		# Check for during Preheat Time
			elif (self.time_now >= self.reach_preheat_time[schedule_index]) and (self.time_now <= self.start_time[schedule_index]) :
				self.target_temp = self.pre_heat_temp[schedule_index] - (self.pre_heat_slope_down[schedule_index] * \
					(self.time_now - self.reach_preheat_time[schedule_index]))
				self.target_full_power = self.target_temp
		# Check for in a session
			elif (self.time_now >= self.start_time[schedule_index]) and (self.time_now <= self.session_end_time[schedule_index]) :
				self.target_temp = self.in_use_temp[schedule_index]
				self.target_full_power = self.target_2nd_after[schedule_index]
		# Must be an Error
			else:
				self.error_message = str(self.time_now) + "In an on Time but could not resolve when"
		else:
			self.error_message = str(self.time_now) + "Not either Found Minimum or Between"
		self.target_full_power = round(self.target_full_power,3)
		self.target_temp = round(self.target_temp,3)
		return


class class_smartplug():
	def __init__(self,number_of_plugs):
							# NOTE Set for 2 plugs,  
							# must introduce way to set number if need more 
		self.seen = [False]*number_of_plugs
		self.state  = [1.234]*number_of_plugs		# state on is "1" off "0"
		self.ip = ["not set"]*number_of_plugs 			# ip address
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
					self.power[index] = self.get_json(read_results[index],"power")
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

class class_text_bffr(object):
	# Rotating Buffer Class
	# Initiate with just the size required Parameter
	# Get data with just a position in buffer Parameter
	def __init__(self, size_max, width,name):
		#initialization
		print(" Buffer Init for : ",name," with a size of : ",size_max, " and  width of : ", width)
		self.__source_ref = 0 # a number used to control prevention repeat messages
		self.size_max = size_max
		self.name = name # used for debugging which bugger instance in use
		self.width = width # add one for left column with time stamp                     
		self.dta = [ [ None for di in range(self.width+1) ] for dj in range(self.size_max+1) ]
		self.size = 0
		self.__posn = self.size_max-1
		self.__html_filename = "not set"
		self.__www_filename = "not set"
		self.__ftp_creds = "not set"
		self.__headings = ["Time"]
		self.__pr_values = ["text"] * self.width

	def set_bffr_html_filename(self, html_filename):
		self.__html_filename = html_filename
		
	def set_bffr_html_filename_save_as(self, html_filename_save_as):
		self.__html_filename_save_as = html_filename_save_as

	def set_bffr_www_filename(self,www_filename):
		self.__www_filename = www_filename
	
	def set_bffr_ftp_creds(self,ftp_creds):
		self.__ftp_creds = ftp_creds
		
	def set_bffr_heading(self,heading):
		self.__headings.append(heading)

	def size(self):
		return self.size_max


	def update_bffr(self,values,appnd,ref):
		#append a line of info at the current position plus 1 
		# print("Update Buffer appnd and ref are : ",appnd,ref)
		if appnd + (self.__source_ref != ref):
			#we adding message and incrementing posn
			if self.size < self.size_max-1 :
				self.size += 1
			if self.__posn == self.size_max-1:
				# last insert was at the end so go back to beginning@@
				self.__posn = 0
			else:
				# first increment insert position by one
				self.__posn += 1
				# then insert a line full of values
			self.__source_ref = ref
		else:
			self.__source_ref = ref		
		if len(values) > self.width :
			print("Width Error for :",self.name, len(values) , self.width, values)
			sys_exit()
		for i in range(0,len(values)):
			self.dta[self.__posn][i] = values[i]
			

			 
	def get_line_dta(self, key):
		#return stored element from position relative to current insert position in buffer
		line_dta = [" - "]*self.width 		
		if (self.__posn-key) > -1:
			# need to take values from area before current insert position
			for i in range(self.width):
				line_dta[i] = self.dta[self.__posn-key][i]
			return(line_dta)
		else:
			# need to take values from after current insert position
			for i in range(self.width):
				#following two lines used too debug the calc to get the lower part of status file
				#print("That Calc key,self.size,self.size_max, self.__posn-key,key sum",
				 #  key,self.size,self.size_max, self.__posn-key,(self.__posn-key),self.(size_max + (self.__posn-key))
				line_dta[i] = self.dta[self.size_max + (self.__posn-key)][i]
			return(line_dta)	
			
			
	def get_dta(self):
		# get all the data inserted so far, or the whole buffer
		all_data = [ [ None for di in range(self.width+1) ] for dj in range(self.size_max+1) ]
		for ind in range(0,self.size):
			line_dta = self.get_line_dta(ind)
			# Following line for debug data from Buffer
			# print("get_dta >>>",ind,line_dta)
			for i in range(len(line_dta)):    
				all_data[ind][i] = line_dta[i]
		return(all_data)
				
			
	def pr(self,appnd,ref,values):
		here = "bffr.pr for " + self.name
		make_values = [" -- "]*self.width
		for_screen = str(make_time_text(datetime.now()))
		prtime = datetime.now()
		for_screen = (str(prtime.day).zfill(2) + "/" + str(prtime.month).zfill(2) + 
			"/" + str(prtime.year).zfill(2) + " " + str(prtime.hour).zfill(2) + ":" + 
			str(prtime.minute).zfill(2) + ":" + str(prtime.second).zfill(2))
		make_values[0] = for_screen
		tbl_start = """ <p>
<table style="float: left;" border="1">
<tbody>"""
		tbl_start_line = """<tr>"""
		tbl_end_line = """</tr>"""
		tbl_start_col = """<td>"""
		tbl_end_col= """</td>"""
		tbl_end = """</tbody>
</table>"""

		try:
			for i in range(0,self.width -1):
				make_values[i+1] = str(values[i])
				for_screen = for_screen + " " + str(values[i])
		except:
			print("Error in make values in ...bffr.pr for : ",self.name)
			print("i,values,len(values),self.width",i,values,len(values),self.width)
			sys.exit()
				
		# print to screen and to status log and update html file
		print(self.name + " : " + for_screen)
		self.update_bffr(make_values,appnd,ref)
		with open(self.__html_filename,'w') as htmlfile:
			htmlfile.write("<p>" + self.__html_filename + " : " + make_time_text(datetime.now())  + "</p>\n<p>")
			htmlfile.write(tbl_start + tbl_start_line)
			for ind in range(0,len(self.__headings)):
				htmlfile.write(tbl_start_col + self.__headings[ind] + tbl_end_col)
			htmlfile.write(tbl_end_line)
			bffr_dta = self.get_dta()
			for ind in range(self.size):
				htmlfile.write(tbl_start_line)
				for i in range(self.width):
					htmlfile.write(tbl_start_col + str(bffr_dta[ind][i]) + tbl_end_col)
				htmlfile.write(tbl_end_line)
			htmlfile.write(tbl_end)
		try:
			copyfile(self.__html_filename, self.__www_filename)
		except:
			print ("Cannot copy (Module Line 1207): ", self.__html_filename , " to : " , self.__www_filename)
		# Change "False" to "True" on next line to debug FTP
		FTP_dbug_flag = False
		#if self.name == "wd":
		#	FTP_dbug_flag = True
		#	print(self.__ftp_creds,self.__html_filename_save_as,self.__html_filename)
		ftp_result = send_by_ftp(FTP_dbug_flag,self.__ftp_creds, self.__html_filename_save_as, self.__html_filename,"")
		for pres_ind in range(0,len(ftp_result)):
			pr(FTP_dbug_flag,here, str(pres_ind) + " : ", ftp_result[pres_ind])
		return		
			


