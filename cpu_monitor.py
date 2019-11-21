#!/usr/bin/env python3

#cpu_monitor.py a python3 script to monitor the cpu and control the pimorini fan_shim
#first writen August 2019 this version October 2019

# Standard library imports
#from subprocess import call as subprocess_call
from time import sleep as time_sleep
#from datetime import datetime
from os import getpid
from os import path
#import sys
from sys import argv as sys_argv
from sys import exit as sys_exit
from datetime import datetime
from random import randint as random_randint
from shutil import copyfile
#import subprocess
#import RPi.GPIO as GPIO

import plasma

# Third party imports
# None
# Local application imports
from config import class_config
from text_buffer import class_text_buffer
from cpu import class_cpu
from utility import fileexists,pr,make_time_text
from wd import class_wd
from algorithm_01 import class_control

cpu = class_cpu()
wd = class_wd("cpu_wd")
my_pid = getpid()
init_printout = ["My PID is : " + str(my_pid)]

#Set up Config file and read it in if present
config = class_config()
if fileexists(config.config_filename):		
	init_printout.append("Config taken from file")
	print( "will try to read Config File : " ,config.config_filename)
	config.read_file() # overwrites from file
else : # no file so my_sensorneeds to be written
	config.write_file()
	init_printout.append("New Config File Made with default values, you probably need to edit it")
	
# make a random number string  between 1 and a thousand use to copy html files
random_text_number = str(random_randint(1,1001))
try:
	print("start copy using: ", random_text_number)
	config.status_html_filename = ""
	config.log_html_filename
	copyfile("cpu_log.html", "old/" + "cpu_log" + random_text_number + ".html")
	print("finish copy")
except:
	print("Cannot copy old files")

############################  each below needs o be check if needed or if could be moved into config.cfg		
config.log_on = False
config.temp_log_on = False
config.log_outfile = ""
config.temp_log_outfile = ""
config.scan_count = 0
config.ftplog_count = 0
config.temp_ftplog_count = 0
config.last_ftplog = 0
config.ref_sensor_index = 0
config.dbug = False
config.dbug_ftp = False
config.exit_flag = False
config.new_config_wanted = False
config.scan_count = 0

headings = ["Count","Cpu Load","Temp","Throttle","Fan Speed","Fan Freq","Cpu Freq","Cpu Mem","Cpu Disk","Loop Times","Message"]
cpu_buffer = class_text_buffer(headings,config)

#Fan shim related
plasma.set_clear_on_exit(True)
plasma.set_light_count(1)
plasma.set_light(0, 0, 0, 0)

control = class_control(config)

# Set The Initial Conditions
sub_count = 0.001
the_end_time = datetime.now()
last_total = 0
loop_time = 0
correction = 4.02
# Ensure start right by inc buffer
last_fan_state = True
buffer_increment_flag = False
refresh_time = 4.2*config.scan_delay

went_off = datetime.now()
went_on = datetime.now()
time_on = 0
time_off = 0

while (config.scan_count <= config.max_scans) or (config.max_scans == 0):
	try:
		# Loop Management and Watchdog
		loop_start_time = datetime.now()
		
		# Control
		cpu.get_data()
		control.calc(cpu.temp)
		cpu.set_pwm_control_fan(control.freq,control.speed)
		cpu.control_fan()
		cpu.update_led_temperature(cpu.temp,config.max_temp,config.min_temp,config.brightness)
		
		# Logging;  log count before incrementing
		cpu_buffer.line_values[0] = str(round(config.scan_count + sub_count,3))
		
		# Increment Log Count
		if control.fan_on:
			sub_count = 0.001
			config.scan_count += 1
		else:
			sub_count += 0.001

		#Logging
		cpu_buffer.line_values[1] = str(cpu.cpu_load) + "%"
		cpu_buffer.line_values[2] = str(round(cpu.temp,2) ) + "C"
		cpu_buffer.line_values[3] = str(round(control.throttle,1))+ "%"
		cpu_buffer.line_values[4] = str(round(control.speed,1))+ "%"
		cpu_buffer.line_values[5] = str(round(control.freq,1))+ "Hz"
		cpu_buffer.line_values[6] = str(cpu.cpu_freq.current/1000) + "GHz"
		cpu_buffer.line_values[7] = str(cpu.cpu_mem) + "%"
		cpu_buffer.line_values[8] = str(cpu.cpu_disk) + "%"
		cpu_buffer.line_values[9] = str(round(last_total,6)) +"s/" + str(round(loop_time,6)) +"s"
		
		if not(last_fan_state) and control.fan_on:
			buffer_increment_flag = True
		elif last_fan_state and not(control.fan_on):
			buffer_increment_flag = True
		elif not(last_fan_state) and not(control.fan_on):
			buffer_increment_flag = False
		elif last_fan_state and control.fan_on:
			buffer_increment_flag = True
		else:
			print("wierd error")
			sys_exit()

		if control.fan_on:
			if not(last_fan_state): # Then was off now on
				went_on = loop_start_time
			time_on = round((loop_start_time - went_on).total_seconds(),0) + config.scan_delay	
			cpu_buffer.line_values[10] = "Fan ON"
			last_fan_state = True
			cpu_buffer.line_values[10] = "Fan ON : " + str(time_on)
		else:
			if last_fan_state: # Then was on now off
				went_off = loop_start_time
			time_off = round((loop_start_time - went_off).total_seconds(),0) + config.scan_delay
			last_fan_state = False
			cpu_buffer.line_values[10] = "Fan OFF : " + str(time_off)
			
		cpu_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
	
		# Loop Managemnt and Watchdog

		count_for_WD = int(100*(config.scan_count + sub_count))
		wd.put_wd(count_for_WD,"ok")
		loop_end_time = datetime.now()
		loop_time = (loop_end_time - loop_start_time).total_seconds()
	
		# Adjust the sleep time to aceive the target loop time and apply
		# with a slow acting correction added in to gradually improve accuracy
		if loop_time < config.scan_delay:
			sleep_time = config.scan_delay - loop_time - (correction/1000)
			try:
				time_sleep(sleep_time)
			except KeyboardInterrupt:
				print("........Ctrl+C pressed...")
				sys_exit()
			except ValueError:
				print("sleep_Time Error value is: ",sleep_time, "loop_time: ",
				      loop_time,"correction/1000 : ",correction/1000)
				print("Will do sleep using config.scan_delay")
				time_sleep(config.scan_delay)
			except Exception:
				print("some other error with time_sleep try with config.scan_delay")
				time_sleep(config.scan_delay) 
		last_end = the_end_time
		the_end_time = datetime.now()
		last_total = (the_end_time - last_end).total_seconds()
		error = 1000*(last_total - config.scan_delay)
		correction = correction + (0.05*error)
		#print("Error : ",1000*(last_total - 5),correction)
	except KeyboardInterrupt:
		print(".........Ctrl+C pressed...")
		sys_exit()

	
