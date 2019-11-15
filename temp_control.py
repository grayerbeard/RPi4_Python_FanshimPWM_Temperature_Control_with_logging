#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	temp_control.py
#   

#	Copyright 2016  <djgtorrens@gmail.com>
#  
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation either version 2 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#	MA 02110-1301, USA.

#   This project uses modules to hold all the classes 
#   the files are all named the same as the Class name plus the version number
#   e.g File with the "text buffer class"; the calss is "class_text_buffer" for version 034 is in "text_buffer_034.py"
#
#   Class list
#
#   "wd"    class with functions to write and read data to a file for the Watch dog function
#   "text_buffer"   class with routines to store a rotating buffer and output its contents  
#                 to html files and send by FTP and copy to local web site             
#   "my_sensors" class with functions to read temperature data from sensors  
#   "smartplug"  class to control and monitor tplink HP110 smartplugs
#   
#   There is also a module "utility_034.py" with a few functions.

# Following are ordered alphabetically

# Standard library imports
#following line used for datetime.now()
from datetime import datetime 
from datetime import timedelta as datetime_timedelta
from ftplib import FTP
from getopt import getopt as getopt_getopt
from os import listdir,path,fsync,getpid
from random import randint as random_randint
from shutil import copyfile
from sys import argv as sys_argv
from sys import exit as sys_exit
from time import sleep as time_sleep
#from RPi.GPIO import setmode as GPIO_setmode
#from RPi.GPIO import setup as GPIO_setup
#from RPi.GPIO import PWM as GPIO_PWM
#from RPi.GPIO import OUT as GPIO_OUT
#from RPi.GPIO import BCM as GPIO_BCM

# Third party imports
# None

# Local application imports
from text_buffer import class_text_buffer
from config import class_config

#from module_034 import class_schedule,class_my_sensors,class_smartplug

from schedule import class_schedule
from my_sensors import class_my_sensors
from smartplug import class_smartplug

from utility_037 import fileexists,pr,make_time_text
from wd_037 import class_wd
	
def main(argv):
	global status_buffer
	last_ref = -1
	here = "main"

	my_pid = getpid()
	wd = class_wd("temp_control_wd")

	config = class_config() # initiate to default values
	config.prog_name = str(sys_argv[0][:-3])
	print("Program Name is : ",config.prog_name)
	prg_version = config.prog_name[-3:]
	print("So Version taken as : ",prg_version)
	
	print("start ver " + prg_version + "  PID (Process ID) is : " + str(my_pid))
	
	
	#For debug purposed copy old html files from last run
	
	# make a random number string  between 1 and a thousand
	random_text_number = str(random_randint(1,1001))
	try:
		print("start copy using: ", random_text_number)
		copyfile("index.html", "old/" + prg_version + "index" + random_text_number + ".html")
		copyfile("status.html", "old/" + prg_version + "status" + random_text_number + ".html")
		copyfile("log.html", "old/" +  prg_version + "log" + random_text_number + ".html")
		copyfile("debug.html", "old/" +  prg_version + "debug" + random_text_number + ".html")
		copyfile("wd_log.html", "old/" +  prg_version + "wd_log" + random_text_number + ".html")
		copyfile("wd.p", "old/" +  prg_version + "wd" + random_text_number + ".p")
		print("finish copy")
	except:
		print("Cannot copy old files")
	
	schedule = class_schedule() # initiate class, is used for targets even if values not taken from schedule file
	init_printout = ["My PID is : " + str(my_pid)]
	config.use_schedule = True
	
	#*****************************************************
	# (1) Get the option Flags
	##	config.check = check(config.check)
	options_ok = False
	#try:pr(config.dbug_ftp,here,"config.local_dir_www: ",  config.local_dir_www )
	for x in range(1,2):
		opts, args = getopt_getopt(argv,"cdfhusw")
		options_ok = True
		init_printout.append("No Options Errors")
		# number of sensors most modes
		sensors_max_number = 5
		for opt, arg in opts:
			if opt == '-w':
				#debug the W1 function with extra printouts
				config.dbug_w1 = True
			if opt == '-s':
				#Sauna control
				init_printout.append("Option : " + opt)
				config.sauna = True
				config.use_schedule = False
				#seven seg stuff being removed
				#config.sevenseg = False
				sensors_max_number = 1
			if opt == '-u':
				#underfloor mode
				config.underfloor = True
				config.use_schedule = False
			if opt == '-c':
				# cretae a new Config file and exit
				init_printout.append("Option : " + opt)
				config.new_config_wanted = True
				config.exit_flag = True
			if opt == '-d':
				# extensive dconfig.prog_path = path.dirname(path.realpath(__file__))ebug printouts
				init_printout.append("Option : " + opt)
				config.dbug = True
			if opt == '-f':
				init_printout.append("Option : " + opt)
				config.dbug_ftp = True
			if opt == '-h':
				# print help info on options
				init_printout.append("Option : " + opt)
				init_printout.append("Help on available options")
				init_printout.append("With No Options Control using Schedule File and Smartplugs")
				init_printout.append("-h :Help ")
				init_printout.append("-w :Extra Debug Printouts temperature sensors interface")
				init_printout.append("-s :Sauna Mode Control Heater Via PWM GPIO Output ")
				init_printout.append("-u :Underfloor Heater Mode; Smartplug Control using default Temperature Targets from config file:  ")
				init_printout.append("-c :Make Config file using default values") 
				init_printout.append("-d :Debug mode extensive printouts to screen ") 
				init_printout.append("-f :Debug ftp and file name creation ")
				config.exit_flag = True
			config.ftplog_count = 0

	if config.use_schedule:
		schedule.read_in_schedule_data("schedule.csv")
		time_now_dt = datetime.now()
		schedule.all_to_file("schedule2_all" + prg_version + ".csv")
		test_file = open("test_target_temps" + prg_version + ".csv",'w')
		test_file.write("time,time_formated,target_temp,target_full_power")
		test_file.write("\n")
		base_time = datetime.now() + datetime_timedelta(days=-1)
		for more_minutes in range(1,15000,10):
			time_check = base_time + datetime_timedelta(minutes=more_minutes)
			temp = datetime(1899, 12, 30)    # Note, not 31st Dec but 30th!
			delta = time_check - temp
		# Convert to Excel format
			time_now = float(delta.days) + (float(delta.seconds) / 86400)
			schedule.get_target_temp(time_check,False)
			test_file.write(str(round(time_now,4)) + "," + time_check.strftime('%c') + "," + str(round(schedule.target_temp,2)) \
				+ "," + str(round(schedule.target_full_power,2)))
			test_file.write("\n")

	#Set things up and read in 
	# init(argv) # 6 tasks setting up variables etc

#Start of part that was in int
	#*************.location****************************************
	# (1) set up buffers and sensor data 
	#     and initialise various pr(config.dbug_ftp,here,"config.local_dir_www: ",  config.local_dir_www )
	#
	if config.sauna:
	#	# Headings: Time,Scan#,Target,Ref Temp,On,Offset,Detect Off
		#smart_log_width = 0   ################# ????????????
	#	log_buffer_width = 4 + 3
		
	else:
		# Headings: Time,Scan#,Target,Ref Temp,T1,T2,T3,T4,T5,I1,V1,P1,T1,I2,V2,P2,T2
		#   1,3,5,4,4 
		#smart_log_width = 8    #################### ?????????????
	#	log_buffer_width = 4 + sensors_max_number + smart_log_width
#####
	log_buffer_headings = ["hdg01","hdg02","hdg03","hdg04","hdg05","hdg06","hdg07","hdg08","hdg09","hdg10","hdg11","hdg14","hdg15","hdg16","hdg17","hdg18","hdg19","hdg20","hdg21"]
	log_buffer_flag = True
	log_buffer = class_text_buffer(100,log_buffer_headings,"log",config,log_buffer_flag)
#######

	#if not(config.sauna):
	#	for ind in range(1,sensors_max_number+1):
	#		log_buffer.set_buffer_heading("T" + str(ind))

	#log_buffer.set_buffer_heading("Scan#")
	#log_buffer.set_buffer_heading("Target")
	#log_buffer.set_buffer_heading("Ref Temp")


	#if config.sauna:
	#	log_buffer.set_buffer_heading("On")
	#	log_buffer.set_buffer_heading("Offset")
	#	log_buffer.set_buffer_heading("Detect Off")
	#else:	
	#	log_buffer.set_buffer_heading("I1")
	#	log_buffer.set_buffer_heading("V1")
	#	log_buffer.set_buffer_heading("P1")
	#	log_buffer.set_buffer_heading("T1")

	#	log_buffer.set_buffer_heading("I2")
	#	log_buffer.set_buffer_heading("V2")
	#	log_buffer.set_buffer_heading("P2")
	#	log_buffer.set_buffer_heading("T2")

# Pattern for setting up buffer
#to set up replace "[name]" with the buffer name
#enter headings
#set flag True/False if want csv log file also made and sent
#[name]_buffer_width = [width]
#headings = ["[heading1]","[heading2]","[heading3]", ......]
#[name]_cpu_log_buffer_flag = [True/False] #if also want csv log file 
#[name]_buffer = class_text_buffer(200,headings,"[name]",config,[name]_log_buffer_flag)
#[name]_buffer_values = [""] * ([name]_buffer_width-1)



	#status_buffer_width = 3
	#status_buffer_values = [""] * (status_buffer_width-1)

	########### needed ???????
	#debug_buffer_width = 4 # One More than max number in values array to allow for col with time stamp
	debug_buffer_values = ["not set"] * (debug_buffer_width - 1)
	########################
	
	#debug_buffer = class_text_buffer(200,debug_buffer_width,"debug",config)
	debug_buffer_headings = ["hdg01","hdg02","hdg03","hdg04","hdg05","hdg06","hdg07","hdg08","hdg09","hdg10","hdg11","hdg14","hdg15","hdg16","hdg17","hdg18","hdg19","hdg20","hdg21"]
	debug_buffer_flag = True
	debug_buffer = class_text_buffer(200,debug_buffer_headings,"log",config,debug_buffer_flag)

	#debug_buffer.set_buffer_heading("Scan#")
	#debug_buffer.set_buffer_heading("Line")
	#debug_buffer.set_buffer_heading("Third Thing")
	html_filename = "debug.html"
	html_filename_save_as = config.prog_path + "debug.html"
	www_filename = config.local_dir_www + "debug.html"
	
	####################### old not needed ??
	#debug_buffer.set_buffer_filenames(html_filename,html_filename_save_as,www_filename,config.ftp_creds_filename)
	#####################

	debug_buffer.line_values[0] = "Debug Buffer Set"
	debug_buffer.line_values[1] = "Software version: " + prg_version
	debug_buffer.line_values[2] = ""
	
	#debug_buffer.pr(True,0, datetime.now())
	refresh_time = config.scan_delay + (config.scan_delay/3)
	#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
	debug_buffer.pr(True,0, datetime.now())

	
	#status_buffer = class_text_buffer(100,status_buffer_width,"status",config)
	status_buffer_headings = ["hdg01","hdg02","hdg03","hdg04","hdg05","hdg06","hdg07","hdg08","hdg09","hdg10","hdg11","hdg14","hdg15","hdg16","hdg17","hdg18","hdg19","hdg20","hdg21"]
	status_buffer_flag = True
	status_buffer = class_text_buffer(100,status_buffer_headings,"log",config,status_buffer_flag)


	# was status_buffer.set_buffer_get_heading("Reason")
	# now set to August 9th 2018	print("start")
	#status_buffer.set_buffer_heading("Reason")
	#status_buffer.set_buffer_heading("Message")
	
	my_sensors = class_my_sensors(sensors_max_number)
 
	# (1) (b) 

	config.prog_path = path.dirname(path.realpath(__file__)) + "/"
	config.prog_name = str(sys_argv[0][:-3])
	
	#####################################################################
	config.config_filename = config.prog_path +  "config_" + prg_version + ".cfg"
	#################################################################
	
	print( "Just set config file to : ", config.config_filename)
	
	print("config.local_dir_www with default: ",  config.local_dir_www )
	print("Program and Module names", config.prog_name, config.my_module_name )
	
	# seven seg stuff being removed
	# config.sevenseg = False # user local sevenseg display
	
	starttime = datetime.now()
	timestamp = make_time_text(starttime)
	pr(config.dbug_ftp,here,"This is the time stamp used for log file >>>", timestamp + "<<<<")
	# GPIO pin set up for Sauna Control
	#GPIO_setmode(GPIO_BCM)
	#GPIO_setup(18, GPIO_OUT)
	#pwm_out = GPIO_PWM(18,0.25)
	#pwm_out.start(0)
					
	#*****************************************************
	# (3) set up filenames

	config.set_filename(config.config_filename)
	init_printout.append( "Will look for this config file : " + config.config_filename)
	#set up configuration
	if fileexists(config.config_filename) and config.new_config_wanted:
		init_printout.append("For a default config file please first rename or delete old file")
		config.exit_flag = True
	elif config.new_config_wanted:
		init_printout.append("New Config File Made (" + str(config.config_filename) + ")with default values, now you can edit it")
		config.write_file()
		config.exit_flag = True
	else:
		if fileexists(config.config_filename):		
			init_printout.append("Config taken from file")
			print( "will try to read Config File : " , config.config_filename )
			config.read_file() # overwrites from file
		else : # no file so my_sensorneeds to be written
			config.write_file()
			init_printout.append("New Config File Made with default values, you probably need to edit it")
	
	#initial values set up
	config.ftplog_count = 0
	config.last_target = config.min_target
	config.last_target_full_power = config.min_target
	
	pr(config.dbug_ftp,here,"config.prog_path: ", config.prog_path)
	pr(config.dbug_ftp,here,"config.local_dir_www: ", config.local_dir_www)
	
	config.s_filename = config.prog_path + config.sensor_config_filename
	pr(config.dbug_ftp,here,"config.s_filename: ", config.s_filename )
	my_sensors.set_s_filename(config.s_filename)
	

	config.log_filename = timestamp + "lg.csv"
	pr(config.dbug_ftp,here,"config.log_filename: ", config.log_filename)
	my_sensors.set_log_filename(config.log_filename)
	
	config.log_filename_save_as =  config.prog_path + config.log_directory + config.log_filename
	pr(config.dbug_ftp,here,"config.log_filename_save_as: ",  config.log_filename_save_as )
	my_sensors.set_log_filename_save_as(config.log_directory + config.log_filename)

	config.local_www_log_filename = config.local_dir_www + config.log_directory + config.log_filename
	pr(config.dbug_ftp,here,"config.local_www_log_filename: ",config.local_www_log_filename )
	my_sensors.set_www_log_filename(config.local_www_log_filename)



	config.html_filename =  "index.html"
	pr(config.dbug_ftp,here,"config.html_filename: ",  config.html_filename)
	my_sensors.set_local_html_filename(config.html_filename)

	config.local_www_html_filename = config.local_dir_www + config.html_filename
	pr(config.dbug_ftp,here,"config.local_www_html_filename: ",config.local_www_html_filename )
	my_sensors.set_www_filename(config.local_www_html_filename)


	config.status_html_filename = "status.html"
	pr(config.dbug_ftp,here,"config.status_html_filename: ",  config.status_html_filename)

	config.status_html_filename_save_as = config.prog_path + config.status_html_filename
	pr(config.dbug_ftp,here,"config.status_html_filename_save_as: ",  config.status_html_filename_save_as )

	config.local_www_status_html_filename = config.local_dir_www + config.status_html_filename
	pr(config.dbug_ftp,here,"config.local_www_status_html_filename: ",  config.local_www_status_html_filename )

	config.log_html_filename = "log.html"
	pr(config.dbug_ftp,here,"config.log_html_filename : ",   config.log_html_filename)
	

	config.log_html_filename_save_as = config.prog_path + config.log_html_filename
	pr(config.dbug_ftp,here,"config.log_html_filename_save_as : ",   config.log_html_filename_save_as)

	config.local_www_log_html_filename = config.local_dir_www + config.log_html_filename
	pr(config.dbug_ftp,here,"local_www_log_html_filename : ",   config.local_www_log_html_filename)



	############### ????????????
	# status_buffer.set_buffer_filenames(config.status_html_filename,config.status_html_filename_save_as,config.local_www_status_html_filename,config.ftp_creds_filename)
	###################### ????
	##############
	# log_buffer.set_buffer_filenames(config.log_html_filename,config.log_html_filename_save_as,config.local_www_log_html_filename,config.ftp_creds_filename)
	####################
	my_sensors.set_status_html_filename(config.status_html_filename)
	my_sensors.set_log_html_filename(config.log_html_filename)
	my_sensors.set_ftp_creds(config.ftp_creds_filename)
	

	#*****************************************************
	# (3) Load in Sensor Data
	#	(If no file then save defaults to config.cfg file)

	if fileexists(config.s_filename): 
		# if there is a file with sensor data read it in
		my_sensors.read_file()
		init_printout.append("Sensor data file data read in")
		new_codes_count = my_sensors.get_temps()
		#then if there are any new we have not seen before write to the sensor file
		if new_codes_count >0 :
			init_printout.append("New Sensors found "+ str(new_codes_count) + " new" )
			my_sensors.write_file(new_codes_count,False)
			init_printout.append("New Sensor data written to file")
	elif len(W1ThermSensor.get_available_sensors()) < 1 : # Check for any sensors
		init_printout.append("No Temp Sensors found check connections")
		config.exit_flag = True
	else: # Wi write to a sensor file
		new_codes_count = my_sensors.get_temps()
		print("No File and new codes found - new_codes_count, my_sensors.width : ", new_codes_count, my_sensors.width)
		my_sensors.write_file(new_codes_count,True)		

	my_sensors.set_sensor4readings(config.sensor4readings)

	#*****************************************************
	# (4) set up empty lists to hold smartplug info
	#		(see "class_smartplug" for information)
	#  NOTE: Class is set from here for 2 (two) plugs
	smartplug = class_smartplug(4)
	smartplug.timeout = 750000 # Initial Value for Timeout in Microseconds (1000000 is 1 second)
	config.number_heaters = 0
	
	if smartplug.validIP(config.heaterIP0):
		smartplug.ip[config.number_heaters] = config.heaterIP0
		smartplug.heater_power_scale[config.number_heaters] = config.heaterIP0_power_scale
		config.number_heaters +=1
		print("Valid IP0 : ",config.heaterIP0)
	else:
		print("Invalid IP0 : ",config.heaterIP0)

	if smartplug.validIP(config.heaterIP1):
		smartplug.ip[config.number_heaters] = config.heaterIP1
		smartplug.heater_power_scale[config.number_heaters] = config.heaterIP1_power_scale
		config.number_heaters +=1
		print("Valid IP1 : ",config.heaterIP1)
	else:
		print("Invalid IP1 : ",config.heaterIP1)

	if smartplug.validIP(config.heaterIP2):
		smartplug.ip[config.number_heaters] = config.heaterIP2
		smartplug.heater_power_scale[config.number_heaters] = config.heaterIP2_power_scale
		config.number_heaters +=1
		print("Valid IP2 : ",config.heaterIP2)
	else:
		print("Invalid IP2 : ",config.heaterIP2)

	if smartplug.validIP(config.heaterIP3):
		smartplug.ip[config.number_heaters] = config.heaterIP3
		smartplug.heater_power_scale[config.number_heaters] = config.heaterIP3_power_scale
		config.number_heaters +=1
		print("Valid IP3 : ",config.heaterIP3)
	else:
		print("Invalid IP3 : ",config.heaterIP3)					
	
	# Initial setup Complete so write messages
	for initial_ind in range(0,len(init_printout)):
		status_buffer.line_values[0] = "Init Report: "
		status_buffer.line_values[1] = init_printout[initial_ind]
		refresh_time = config.scan_delay + (config.scan_delay/3)
		#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
		status_buffer.pr(True,0, datetime.now())		

	if config.exit_flag:
		sys_exit()
  

	#*****************************************************
	# (6) set up log file using parameters from config.cfg
	#		(file based is based on current time)

	if len(config.log_directory) > 0:
		config.log_outfile = open(config.log_filename_save_as,'w')
		config.log_on = True
	else:
		config.log_on = False
		config.log_filename = None
		config.log_outfile = ""

	#*****************************************************
	# (6) Make su	config.check = check(config.check)re the Gpio and thermometer modules are loaded
	#		()
	
	#Commented out for test
	#subprocess.call(['sudo','modprobe', 'w1-gpio'])
	#subprocess.call(['sudo','modprobe', 'w1-therm'])
	

	#*****************************************************
	# (17) set up error codes
	#		()

	error=["OK","1File only","2New no Data","3Timeout","4CRC er",
		"5Read Err","6Retry Err","7Error","8No Data","9No Dev","10Disconn"]
	
	# if there is a schedule file read it in, if not quit
	sch_filename = config.prog_path + "schedule.csv" 
	if config.use_schedule:
		sch_filename = config.prog_path + "schedule.csv"
		if fileexists(sch_filename):
			status_buffer.line_values[0] = "Schedule Found in: "
			status_buffer.line_values[1] = sch_filename
			refresh_time = config.scan_delay + (config.scan_delay/3)
			#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
			status_buffer.pr(True,1, datetime.now())
			schedule = class_schedule()
			schedule.read_in_schedule_data(sch_filename)
		else:	
			quit ( "No Schedule File Found")
 
	#Main Loop
	change_flag = False
	config.scan_count = 1
	config.sensor_present = False
	# Scan for max_scan times or for ever if config.max_scans = 0
	
	print("Start Main" )
	
	while (config.scan_count <= config.max_scans) or (config.max_scans == 0):
		# For clarity when using debug to see start of scan
		pr(config.dbug,here, " ----- ",  "                                    ----- ")			
		# now get data from all the sensor that are connected
		new_codes_count = my_sensors.get_temps()
		# then if there are any new we have not seen before write to the sensor file
		if new_codes_count >0 :
			my_sensors.write_file(new_codes_count,len(my_sensors.code) == new_codes_count)
		for z in range(0,len(my_sensors.code),1):
			if my_sensors.connected[z]:
				pr(config.dbug_w1,here,"sensor : " + str(my_sensors.number[z]) + " returned :", my_sensors.reading[z])
			if (abs(my_sensors.last_logged[z] - my_sensors.reading[z])) > float(config.change4log): 
				change_flag = True
				if config.scan_count > 1 :
					my_sensors.last_logged[z] = my_sensors.reading[z]
			if my_sensors.last_logged_error_number[z] != my_sensors.error_number[z]:
				change_flag = True 

# **************************** 
#  Get target temperature
#****************************	
		time_now = datetime.now()
		
		not_underfloor = False
		
		if config.sauna:
			# If in Sauna mode then there is only the one target temperaturetaken from the config file
			# In future could change this to have a scheduled time for the Sauna in a schedule file
			schedule.target_temp = config.default_target
			schedule.target_full_power = config.default_target_full_power
			if config.scan_count < 2 :
				config.target_offset = - 0.1*(schedule.target_temp - schedule.target_full_power)
			if schedule.target_full_power > (schedule.target_temp - 1):
				schedule.target_full_power = schedule.target_temp - 1
				status_buffer.line_values[0] = "Target Full Power not at least 1 deg below Target"
				status_buffer.line_values[1] = "Using : " + schedule.target_full_power + " for target full power"
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)				
				status_buffer.pr(True,3, datetime.now())	
		elif config.use_schedule:	
			# Not in sauna mode so get target temps from schedule file
			schedule.get_target_temp(time_now,config.dbug)
			if schedule.error_message != "OK" :
				status_buffer.line_values[0] = "Schedule Error. Will use last if they < max and > min allowed"
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
				status_buffer.line_values[1] = schedule.error_message
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
				status_buffer.pr(True,1, datetime.now())
			# Check that the full power is not greater than the target as then control would not work right
			status_buffer.line_values[0] = ""
			if schedule.target_full_power > config.max_target :
				schedule.target_full_power = config.max_target
				status_buffer.line_values[0] = "Target Full Power reduced to max "
			elif schedule.target_full_power < config.min_target :
				schedule.target_full_power = config.min_target
				status_buffer.line_values[0] = "Target Full Power increased to min "
			if schedule.target_temp > config.max_target :
				schedule.target_temp = config.max_target
				status_buffer.line_values[0] = status_buffer.line_values[0] + "Target Temp reduced to max "
			elif schedule.target_full_power < config.min_target :
				schedule.target_temp = config.min_target
				status_buffer.line_values[0] = status_buffer.line_values[0] + "Target Temp increased to min "
			if schedule.target_full_power > schedule.target_temp:
				schedule.target_full_power = schedule.target_temp
				status_buffer.line_values[0] = status_buffer.line_values[0] + "Target Full Power was not < Target"
			if status_buffer.line_values[0] != "" :
				status_buffer.line_values[1] = "Using : " + str(schedule.target_full_power) + " for full pwr with "+ \
					str(schedule.target_temp) + " as target"
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
				status_buffer.pr(True,3, datetime.now())	
			if (config.last_target != schedule.target_temp) or  \
				(config.last_target_full_power != schedule.target_full_power):
				if abs(schedule.target_temp - config.last_target) <  0.25 :
					status_re_write_flag = False
					status_buffer.line_values[0] = "Target Change"
				else:
					status_re_write_flag = True
					status_buffer.line_values[0] = "Target Change"
				status_buffer.line_values[1] = str(config.last_target) + "/" + str(config.last_target_full_power) \
					+ " to " + str(schedule.target_temp) + 	"/" + str(schedule.target_full_power)
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
				status_buffer.pr(status_re_write_flag,3, datetime.now())	
				config.last_target = schedule.target_temp
				config.last_target_full_power = schedule.target_full_power
		#So in underfloor on heat mode so set temperatures as if in sauna mode from the config file		
		elif config.underfloor:
			status_buffer.line_values[0] = ""
			schedule.target_temp = config.default_target
			schedule.target_full_power = config.default_target_full_power
			if schedule.target_full_power > (schedule.target_temp - 1):
				schedule.target_full_power = schedule.target_temp - 1
				status_buffer.line_values[0] = "UF Target Full Power not at least 1 deg below Target"
				status_buffer.line_values[1] = "UF Using : " + schedule.target_full_power + " for target full power"
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
				status_buffer.pr(True,3, datetime.now())	
			if schedule.target_temp > config.max_target :
				schedule.target_temp = config.max_target
				status_buffer.line_values[0] = status_buffer.line_values[0] + "UF Target Temp reduced to max "
			elif schedule.target_full_power < config.min_target :
				schedule.target_temp = config.min_target
				status_buffer.line_values[0] = status_buffer.line_values[0] + "UF Target Temp increased to min "
			if schedule.target_full_power > schedule.target_temp:
				schedule.target_full_power = schedule.target_temp
				status_buffer.line_values[0] = status_buffer.line_values[0] + "UF Target Full Power was not < Target"
			if status_buffer.line_values[0] != "" :
				status_buffer.line_values[1] = "UF Using : " + str(schedule.target_full_power) + " for full pwr with "+ \
					str(schedule.target_temp) + " as target"
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
				status_buffer.pr(True,3, datetime.now())	
			if (config.last_target != schedule.target_temp) or  \
				(config.last_target_full_power != schedule.target_full_power):
				# print("Change detected")
				if abs(schedule.target_temp - config.last_target) <  0.25 :
					status_re_write_flag = False
					status_buffer.line_values[0] = "UF Target Change"
				else:
					status_re_write_flag = True
					status_buffer.line_values[0] = "UF Target Change"
				# status_buffer.line_values[0] = "Target Change"
				status_buffer.line_values[1] = str(config.last_target) + "/" + str(config.last_target_full_power) \
					+ " to " + str(schedule.target_temp) + 	"/" + str(schedule.target_full_power)
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
				status_buffer.pr(status_re_write_flag,3, datetime.now())	
				config.last_target = schedule.target_temp
				config.last_target_full_power = schedule.target_full_power
				
# ****************************
# Start of heater Control *
# ****************************
		
		#  Check if reading indictates if heaters should be turned on of off		
		config.control_error = (my_sensors.reading[config.ref_sensor_index] - \
			(schedule.target_temp-config.target_offset))/config.control_hysteresis
		if config.sauna :
			if (len(my_sensors.reading) > 0) and (config.ref_sensor_index != -1 ):
				
				# seven seg modes eyc being removed
				#if config.sevenseg :
				#	show_numbers(schedule.target_temp, my_sensors.reading[config.ref_sensor_index] )
					
					
				if my_sensors.reading[config.ref_sensor_index] > schedule.target_full_power:	
					config.reached_target = True
				if (my_sensors.reading[config.ref_sensor_index] < schedule.target_full_power) and config.reached_target:
					config.detect_off_count += 1
				if my_sensors.reading[config.ref_sensor_index] > \
						schedule.target_temp + config.target_offset + (schedule.target_temp - schedule.target_full_power) :
					config.sauna_on = 0
					pwm_out.ChangeDutyCycle(config.percent_full_power * config.sauna_on)
					config.detect_off_count = 0
				else:
					if my_sensors.reading[config.ref_sensor_index] < schedule.target_full_power + config.target_offset:
						config.sauna_on = 1
						pwm_out.ChangeDutyCycle(config.percent_full_power * config.sauna_on)
						if config.reached_target:
							config.detect_off_count += 1
					else:
						# calc on ratio where 100% on is 1
						offset_target = schedule.target_temp + config.target_offset
						diff_targets = schedule.target_temp - schedule.target_full_power
						reading = my_sensors.reading[config.ref_sensor_index]
						config.sauna_on = ((offset_target + (diff_targets)) - reading) \
							/(2*(diff_targets))
						
						if config.sauna_on > 1:
							config.sauna_on = 1
							print("reduce to 1")
						if config.sauna_on < 0:
							print("increase to 0")
							config.sauna_on = 0
							
						pwm_out.ChangeDutyCycle(config.percent_full_power * config.sauna_on)
						
						# Integral Control using an offset of the target temperature
						# max offset is limited to difference betrween target and full power target
						config.target_offset = config.target_offset + (config.target_integral* \
							(schedule.target_temp-my_sensors.reading[config.ref_sensor_index]))
						if config.target_offset > (schedule.target_temp - schedule.target_full_power):
							config.target_offset =  (schedule.target_temp - schedule.target_full_power)
						if config.target_offset < - (schedule.target_temp - schedule.target_full_power):
							config.target_offset = - (schedule.target_temp - schedule.target_full_power)
			else:
				print("No Ref",  len(my_sensors.reading),  config.ref_sensor_index )
				status_buffer.line_values[0] = "Error Message"
				status_buffer.line_values[1] = ("No ref line 469" + str(len(my_sensors.reading)) +
				                          ":" + str(config.ref_sensor_index)) 
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
				status_buffer.pr(True,4, datetime.now())
		else :	
			if (len(my_sensors.reading) > 0) and (config.ref_sensor_index != -1 ):

				s_time = datetime.now()
				s_hour = s_time.hour
				
				# If temperature is above Target Temperature then turn all heaters off
								
				if my_sensors.reading[config.ref_sensor_index] > schedule.target_temp :
					#print("Turn off", my_sensors.reading[config.ref_sensor_index],schedule.target_temp + float(config.control_hysteresis))
					pr(config.dbug_w1,here,"Turn off smart plugs at temp: ", my_sensors.reading[config.ref_sensor_index])
					for ipind in range(0,config.number_heaters):
						responce = smartplug.turn_off_smartplug(ipind)
						if responce == "error":
							print("Error Plug Turn Off for index : " + str(ipind))
						else:
							smartplug.turn_off_time_taken = smartplug.calculate_time("Turn off")
							pr(config.dbug,here,"Plug " + str(ipind),"off OK" + " Responce is : " +  responce)
				
				# If temp below target_full_power turn all on
				
				elif my_sensors.reading[config.ref_sensor_index] < schedule.target_full_power :
					pr(config.dbug,here,"Turn on all" + str(my_sensors.reading[config.ref_sensor_index]) \
					,schedule.target_full_power - float(config.control_hysteresis))
					for ipind in range(0,config.number_heaters):
						responce = smartplug.turn_on_smartplug(ipind)
						if responce == "error":
							print("Error Plug Turn On for index : " + str(ipind))
						else:
							smartplug.turn_on_time_taken = smartplug.calculate_time("Turn on")
							pr(config.dbug,here,"Plug " + str(ipind),"on OK" + " Responce is : " + responce)
				
				# If between Target Temp and Full power so need to turn on just one heater
				
				elif (my_sensors.reading[config.ref_sensor_index] > schedule.target_full_power) and \
					(my_sensors.reading[config.ref_sensor_index] < schedule.target_temp):
					for ipind in range(0,config.number_heaters):
						if ipind == config.one_heater_select:
							responce = smartplug.turn_on_smartplug(ipind)
							if responce == "error":
								print("Error Plug Turn On for index : " + str(ipind))
							else:
								smartplug.turn_on_time_taken = smartplug.calculate_time("Turn on")
								pr(config.dbug,here,"Plug " + str(ipind),"on OK" + " Responce is : " + responce)    
						else:
							responce = smartplug.turn_off_smartplug(ipind)
							if responce == "error":
								print("Error Plug Turn Off for index : " + str(ipind))
							else:
								smartplug.turn_off_time_taken = smartplug.calculate_time("Turn off")
								# error ext line found 5 not 4 values April 3rd 2019
								pr(config.dbug,here,"Plug " + str(ipind),"off OK" + " Responce is : " + responce)

			else:
				print ("No Control")
				status_buffer.line_values[0] = "Error Message"
				status_buffer.line_values[1] = "No ref line 691"
				refresh_time = config.scan_delay + (config.scan_delay/3)
				#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
				status_buffer.pr(True,5, datetime.now())
# ****************************
#  End  of heater Control *
# ****************************

		# create the index.html file and then send it to local and remote websites
		my_sensors.send_html_by_ftp(config,smartplug,schedule.target_temp,schedule.target_full_power)
		
		# config.ftplog_count will be 0 first time only so log at start then reset to 1 
		# counts up to config.ftp_log_max_count to trigger log if ther eis no change
		#print("change_flag, log count, max,config.scan_count", str(change_flag), config.ftplog_count, config.ftp_log_max_count,config.scan_count)
		if change_flag or (config.scan_count == config.max_scans) or (config.scan_count == 0) or (config.ftplog_count >= config.ftp_log_max_count):
			my_sensors.set_status_text(config) # figure out the status text for the temperature sensors
			if config.log_on:
				#print("Doing Log with config.ftplog_count = ",config.ftplog_count)
				my_sensors.log_to_file(config,smartplug,schedule.target_temp, 
					my_sensors.reading[config.ref_sensor_index],config.dbug,smart_log_width) 
				pr(config.dbug,here," *** config.ftplog_count : ",config.ftplog_count)
				my_sensors.send_log_by_ftp(config.dbug_ftp,config.log_directory,config.ftp_timeout)
				my_sensors.copy_log_to_www(config.dbug_ftp)
				config.last_ftplog = config.scan_count
			log_buffer_append_flag = True	
			config.ftplog_count = 0
		else:
			config.ftplog_count += 1
			#print("Not logging so incremented count to: ",config.ftplog_count, "Then print to screen")
			if config.scan_count < 3 : # config.ftp_log_max_count:
				#print("Less Than 2 >> True",config.scan_count)
				log_buffer_append_flag = True
			else:
				#print("2 or More >> False",config.scan_count)
				log_buffer_append_flag = False
		if config.sauna != True:
			# Make sure up to date with Smartplug info for log html file
			responce = smartplug.get_smartplug_status(config.dbug,config)
			if responce == "error":
				print(str(smartplug.get_status_error_count) + " Error(s) Getting Smartplug Status")
				smartplug.get_status_error_count = 0
			else:
				pr(config.dbug,here,"Got Status OK" + " Responce is : ",responce)
		


		log_buffer.line_values = my_sensors.make_printout_for_screen(schedule.target_temp,my_sensors.reading[config.ref_sensor_index],config,smartplug)
		refresh_time = config.scan_delay + (config.scan_delay/3)
		#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
		log_buffer.pr(log_buffer_append_flag,0,datetime.now())
		#log_buffer.pr(log_buffer_append_flag,0, my_sensors.make_printout_for_screen(schedule.target_temp,my_sensors.reading[config.ref_sensor_index],config,smartplug))


		# Following can be used to log the time taken to talk to smart plugs
		#debug_buffer.line_values[0] = "Scan : " + str(config.scan_count)
		#if config.sauna != True:
		#	debug_buffer.line_values[0] = debug_buffer.line_values[0] + " GetStat Errs: " + str(smartplug.get_status_error_count)
		#debug_buffer.line_values[1] = "Maximum Smartplug Time Was " + str(round(smartplug.max_time/1000000,4)) + "secs"
		#debug_buffer.line_values[2] = "Timeout Is " + str(round(smartplug.timeout/1000000,4)) + "secs"
		#refresh_time = config.scan_delay + (config.scan_delay/3)
		#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
		#debug_buffer.pr(True,0, datetime.now())
		#print("config.dbug :",config.dbug)
		#debug_buffer.line_values[0] = "Turn Off Time " + str(round(smartplug.turn_off_time_taken/1000000,4)) + "secs"
		#debug_buffer.line_values[1] = "Turn On Time " +  str(round(smartplug.turn_on_time_taken/1000000,4)) + "secs"
		#debug_buffer.line_values[2] = "Read " + str(round(smartplug.do_read_time_taken/1000000,4)) + "secs  " + \
		#					   "Info " + str(round(smartplug.do_info_time_taken/1000000,4)) + "secs"
		#refresh_time = config.scan_delay + (config.scan_delay/3)
		#example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
		#debug_buffer.pr(True,0, datetime.now())
		
		#reset change flag and operate delay before next scan
		change_flag = False
		last_ended  = make_time_text(datetime.now())	
		# if in sauna mode and between sauna control does its own delays
		
		# write file to be used by Watch Dog Program
		print("sending from temp control : ",config.scan_count)
		wd.put_wd(config.scan_count,"ok")
		
		# Sleep for a delay
		print("Before Sleep for : ",config.scan_delay)
		time_sleep(config.scan_delay)
		print("After Sleep")
		
		# increment count
		config.scan_count += 1
		
		# Shut down if Sauna Heater Detected as off and temperature dropping
		if config.sauna and (config.detect_off_count > 10) :
			call("sudo shutdown -h now", shell=True)
			
	return 0

if __name__ == '__main__':
	main(sys_argv[1:])


