#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	My sensors.py november 2019
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
			htmlfile.write(ftp_text_linestart + " Program Name:  " + ftp_text_between  \
											+ config.prog_name + ftp_text_line_end)
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
		ftp_result = send_by_ftp(FTP_dbug_flag,self.__ftp_creds, self.__html_filename, "index.html","",config.ftp_timeout)
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
			config.log_outfile.write("Time,")
			config.log_outfile.write("Count,")
			config.log_outfile.write("Target,")
			config.log_outfile.write("Ref Sensor,")
			if config.sauna:
				config.log_outfile.write("On,")
				config.log_outfile.write("Offset,")
				config.log_outfile.write("Detect Off")
				config.log_outfile.write("\n")
			else:
				for hdg_ind in range(1,(self.max_width+1)):
					config.log_outfile.write("T" + str(hdg_ind)+",")
				config.log_outfile.write("I1,")
				config.log_outfile.write("V1,")
				config.log_outfile.write("P1,")
				config.log_outfile.write("T1,")
				config.log_outfile.write("I2,")
				config.log_outfile.write("V2,")
				config.log_outfile.write("P2,")
				config.log_outfile.write("T2,")
				config.log_outfile.write("\n")
		self.__log_count += 1
		logtime = datetime.now()
		logtime_text = (str(logtime.day).zfill(2) + "/" + str(logtime.month).zfill(2) + 
			"/" + str(logtime.year).zfill(2) + " " + str(logtime.hour).zfill(2) + ":" + 
			str(logtime.minute).zfill(2) + ":" + str(logtime.second).zfill(2))
		config.log_outfile.write(logtime_text)
		if (self.sensor_present == False):
			config.log_outfile.write(" : no sensors with Trg Temp of : " + str(target_temp) + "\n")
		else:
			config.log_outfile.write("," + str(self.__log_count) + ",")
			config.log_outfile.write(str(target_temp) + ",")
			config.log_outfile.write(str(ref_sensor) + ",")
			if config.sauna:
				config.log_outfile.write(str(config.percent_full_power * config.sauna_on)+ ",")
				config.log_outfile.write(str(config.target_offset) + ",")
				config.log_outfile.write(str(config.detect_off_count))
			else:
				for z in range(0,self.max_width,1):
					#record the data last saved for this sensor
					#send data to the file only if the sensor is connected
					config.log_outfile.write(str(self.status_text[z]) + ",")
					self.last_logged[z] = self.reading[z]
					self.last_logged_error_number[z] = self.error_number[z]
				config.log_outfile.write(str(smartplug_info.current[0]))
				config.log_outfile.write("," + str(smartplug_info.voltage[0]))
				config.log_outfile.write("," + str(smartplug_info.power[0]))
				config.log_outfile.write("," + str(smartplug_info.total[0]))
				pr(dbug_flag,here,"Total power going to log file", smartplug_info.total[0])
				#config.log_outfile.write("," + str(smartplug_info.error[1]))
				#config.log_outfile.write("," + str(smartplug_info.state[1]))
				config.log_outfile.write("," + str(smartplug_info.current[1]))
				config.log_outfile.write("," + str(smartplug_info.voltage[1]))
				config.log_outfile.write("," + str(smartplug_info.power[1]))
				config.log_outfile.write("," + str(smartplug_info.total[1]))
				pr(dbug_flag,here,"Total power going to log file", smartplug_info.total[1])
				#config.log_outfile.write("," + str(smartplug_info.error[1]))
			config.log_outfile.write("\n")
			config.log_outfile.flush()
		return
		
	def send_log_by_ftp(self,FTP_dbug_flag,remote_log_dir,timeout):
		here = "my_sensors.send_log_by_ftp"
		ftp_result = send_by_ftp(FTP_dbug_flag,self.__ftp_creds, self.__log_filename_save_as, \
			self.__log_filename,remote_log_dir,timeout)
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


