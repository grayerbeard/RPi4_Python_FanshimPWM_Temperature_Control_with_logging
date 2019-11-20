d#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	tsauna.py for temperature control of a sauna stove
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
	wd_filename = "temp_control_wd"
	wd = class_wd("wd_filename")
	config = class_config() # initiate to default values
if fileexists(config.config_filename):		
	init_printout.append("Config taken from file")
	print( "will try to read Config File : " ,config.config_filename)
	config.read_file() # overwrites from file
else : # no file so my_sensorneeds to be written
	config.write_file()

	log_buffer_headings = ["Time","Scan","Ref Temp","PWM %","PWM Freq"]
	log_buffer_flag = True
	log_buffer = class_text_buffer(log_buffer_headings,config)

	starttime = datetime.now()
	timestamp = make_time_text(starttime)
	pr(config.dbug_ftp,here,"This is the time stamp used for log file >>>", timestamp + "<<<<")
	# GPIO pin set up for Sauna Control
	#GPIO_setmode(GPIO_BCM)
	#GPIO_setup(18, GPIO_OUT)
	#pwm_out = GPIO_PWM(18,0.25)
	#pwm_out.start(0)
					



 
	#Main Loop
	change_flag = False
	config.scan_count = 1
	config.sensor_present = False
	# Scan for max_scan times or for ever if config.max_scans = 0
	
	print("Start Main" )
	
	while (config.scan_count <= config.max_scans) or (config.max_scans == 0):
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


