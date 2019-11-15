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
from cpu_monitor_config import class_config
from text_buffer import class_text_buffer
from cpu import class_cpu
from utility import fileexists,pr,make_time_text
from wd import class_wd

cpu = class_cpu()
wd = class_wd("cpu_wd")
my_pid = getpid()
init_printout = ["My PID is : " + str(my_pid)]

#Set up Config file and read it in if present
config = class_config("/home/pi/ftp_creds/ftp_creds.csv","/var/www/html/","log/",5,0.5)
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

config.scan_count = 0

cpu_buffer_width = 11

headings = ["Count","Cpu Load","Temp","Throttle","Fan Speed","Cpu Freq","Cpu Mem","Cpu Disk","Times","Msg"]
cpu_buffer = class_text_buffer(50,headings,config)
cpu_buffer_values = [""] * (cpu_buffer_width-1)


#Fan shim related
plasma.set_clear_on_exit(True)
plasma.set_light_count(1)
plasma.set_light(0, 0, 0, 0)

#Target Range temperatures
max_temp =  69.0
min_temp = 61.0   
lower_mid_temp =   (max_temp  + min_temp)/2  - ((max_temp - min_temp)/4)
upper_mid_temp =   (max_temp  + min_temp)/2  + ((max_temp - min_temp)/4)
lower_min_temp =   min_temp - ((max_temp  - min_temp)/2)

print(lower_min_temp,min_temp,lower_mid_temp,upper_mid_temp,max_temp)

target_loop_time = 5   # target cycle time in secounds, code self adjusts to acheive this
min_speed = 75 # minimum percent speed
max_speed = 90 # max percent PWM speed
print("lower_mid_temp is : ",lower_mid_temp)
brightness = 80
freq = 2
check = 0.001
speed = 0 
throttle = 0
try_throttle_calc_smoothed = 0
last_cpu_temp = min_temp
buffer_increment_flag = True
the_end_time = datetime.now()
last_total = 0
loop_time = 0
correction = 4.02

#print("FTP Cred File is: ",config.ftp_creds_filename)
#print("Config filename: ",config.config_filename)
#sys_exit()



while (config.scan_count <= config.max_scans) or (config.max_scans == 0):
	print("Count/Max",config.scan_count,config.max_scans)
	try:
		loop_start_time = datetime.now()
		cpu.get_data()
		check += 0.001
		count_for_WD = int(100*(config.scan_count + check))
		try_throttle_calc = 100 * (cpu.temp - min_temp)/(max_temp - min_temp)
		try_throttle_calc_smoothed = try_throttle_calc_smoothed + 0.1*(try_throttle_calc - try_throttle_calc_smoothed)
		change = cpu.temp - last_cpu_temp
		if change > 1.1:
			print("---------------- Big CTemp Increase : ",last_cpu_temp, " to ",cpu.temp, " so ", change)
		last_cpu_temp = cpu.temp
	
		# Check CPU temperature situation to use in below IF  statements
		# Display data occasionally
		c_or_1 = check >= 0.998
		# Turn off Fan when on and below target range
		c_or_2 = (throttle > 0) and (cpu.temp<lower_min_temp)  # e.g. if using 61 to 69 then 57
		# Turn fan on when temperature increasing fast
		c_or_3 = (change > 2.1) and (cpu.temp > lower_mid_temp)# e.g. if using 61 to 69 then 63
		# Turn fan on when temperature approaching top of target range.
		c_or_4 = cpu.temp >= upper_mid_temp 				   # e.g. if using 61 to 69 then 67	
	
		if c_or_1 or c_or_2 or c_or_3 or c_or_4:
	
			buffer_increment_flag = True
	
			cpu.calc_averages()
	
			if cpu.temp >= max_temp:
				throttle = 100
			elif cpu.temp<= min_temp:
				throttle = 0
			elif cpu.temp >= upper_mid_temp:
				# use lastest info when temperature high
				throttle = try_throttle_calc
			elif try_throttle_calc_smoothed > 0:
				# use smoothed data when temperature lower and smoother value over zero
				throttle = try_throttle_calc_smoothed
			else:
				throttle = 6
	
			if throttle <= 0 :
				speed = 0
				freq = 2
			else:
				speed = min_speed + (throttle*(max_speed-min_speed)/100)
				freq = 5
	
			cpu.set_pwm_control_fan(freq,speed)
	
			cpu.update_led_temperature(cpu.temp,max_temp,min_temp,brightness)
	
			cpu_buffer.line_values[0] = str(round(config.scan_count + check,3))
			cpu_buffer.line_values[1] = str(cpu.average_load) + "%"
			cpu_buffer.line_values[2] = str(round(cpu.temp,2) ) + "C"
			cpu_buffer.line_values[3] = str(round(throttle,1))+ "%"
			cpu_buffer.line_values[4] = str(round(speed,1))+ "%"
			cpu_buffer.line_values[5] = str(cpu.cpu_freq.current/1000) + "GHz"
			cpu_buffer.line_values[6] = str(cpu.cpu_mem) + "%"
			cpu_buffer.line_values[7] = str(cpu.cpu_disk) + "%"
			cpu_buffer.line_values[8] = str(round(last_total,6)) +"s/" + str(round(loop_time,6)) +"s"
			cpu_buffer.line_values[9] = str(int(c_or_1)) + str(int(c_or_2)) + str(int(c_or_3)) + str(int(c_or_4))
	
			refresh_time = config.scan_delay + (config.scan_delay/3)
			cpu_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
	
			config.scan_count += 1
			check = 0
		
		else:
			#Uncomment following Two lines to observe if curious
			#print(" Count : ",round(config.scan_count+check,2),cpu.get_av_cpu_load_so_far(),"Temp : ",
			#	round(cpu.temp,2),"Throttle/smoothed : ",round(try_throttle_calc,2),"/",round(try_throttle_calc_smoothed,2)) 
			cpu_buffer.line_values[0] = str(round(config.scan_count + check,3))
			
			if buffer_increment_flag:
				cpu_buffer.line_values[1] = str(cpu.average_load) + "%"
				cpu_buffer.line_values[2] = str(round(cpu.temp,2) ) + "C"
				cpu_buffer.line_values[3] = str(round(throttle,1))+ "%"
			else:
				cpu_buffer.line_values[1] = str(cpu.cpu_load) + "%"
				cpu_buffer.line_values[2] = str(round(cpu.temp,2) ) + "C"
				cpu_buffer.line_values[3] = str(round(try_throttle_calc,1))+ "%"
			cpu_buffer.line_values[4] = str(round(speed,1))+ "%"
			cpu_buffer.line_values[5] = str(cpu.cpu_freq.current/1000) + "GHz"
			cpu_buffer.line_values[6] = str(cpu.cpu_mem) + "%"
			cpu_buffer.line_values[7] = str(cpu.cpu_disk) + "%"
			cpu_buffer.line_values[8] = str(round(last_total,6)) +"s/" + str(round(loop_time,6)) +"s"
			cpu_buffer.line_values[9] = "NoFlag"
			refresh_time = config.scan_delay + (config.scan_delay/3)
			cpu_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
			if throttle == 0:
				buffer_increment_flag = False
		cpu.control_fan()
		wd.put_wd(count_for_WD,"ok")
		loop_end_time = datetime.now()
		loop_time = (loop_end_time - loop_start_time).total_seconds()
	
		# Adjust the sleep time to aceive the target loop time and apply
		# with a slow acting correction added in to gradually improve accuracy
		if loop_time < target_loop_time:
			sleep_time = target_loop_time - loop_time - (correction/1000)
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
		error = 1000*(last_total - 5)
		correction = correction + (0.05*error)
		#print("Error : ",1000*(last_total - 5),correction)
	except KeyboardInterrupt:
		print(".........Ctrl+C pressed...")
		sys_exit()

	
