#!/usr/bin/env python3

#test_text_buffer.py a python3 script to test the text_buffer module October 2019

# Standard library imports
#from subprocess import call as subprocess_call
from time import sleep as time_sleep
from os import getpid
#from os import path
#from sys import argv as sys_argv
from sys import exit as sys_exit
from datetime import datetime
from random import randint as random_randint
from shutil import copyfile

# Third party imports
# None

# Local application imports
from text_buffer_config import class_config
from text_buffer import class_text_buffer
from utility import fileexists,pr,make_time_text

config = class_config("/home/pi/ftp_creds/ftp_creds.csv","/var/www/html/","log/",5,10)

################################
#print("config.ftp_creds_filename : ",config.ftp_creds_filename)
#my_pid = getpid()
#config.prog_path = path.dirname(path.realpath(__file__)) + "/"
#config.prog_name = str(sys_argv[0][:-3])
#print(config.prog_name)
#config.config_filename = config.prog_name + ".cfg"
#config.set_filename(config.config_filename)
#print("config file is : ",config.config_filename)
###############################################

if fileexists(config.config_filename):		
	print( "will try to read Config File : " ,config.config_filename)
	config.read_file() # overwrites from file
else : # no file so needs to be written
	config.write_file()
	print("New Config file made")

config.scan_count = 0

headings = ["Count","Val1","Val2","Val3","Val4","Val5"]
example_buffer = class_text_buffer(headings,config)

buffer_increment_flag = True

end_time = datetime.now()
last_total = 0
loop_time = 0
correction = 4.02
print("config.scan_delay",config.scan_delay)
while (config.scan_count <= config.max_scans) or (config.max_scans == 0):
	try:
		loop_start_time = datetime.now()
		example_buffer.line_values[0] = str(config.scan_count)
		example_buffer.line_values[1] = str(round(float(example_buffer.line_values[1]) + 0.11,2))
		example_buffer.line_values[2] = str(round(float(example_buffer.line_values[2]) + 0.22,2))
		example_buffer.line_values[3] = str(round(float(example_buffer.line_values[3]) + 0.33,2))
		example_buffer.line_values[4] = str(round(float(example_buffer.line_values[4]) + 0.44,2))
		example_buffer.line_values[5] = str(round(float(example_buffer.line_values[5]) + 0.55,2))
	
		# how often in this test mode buffer is updated rather than just displayed
		test_update_buffer_rate = 4
	
		if(config.scan_count % test_update_buffer_rate == 0):
			buffer_increment_flag = True
		else:
			buffer_increment_flag = False
		refresh_time = config.scan_delay + (config.scan_delay/3)
		example_buffer.pr(buffer_increment_flag,0,loop_start_time,refresh_time)
	
		config.scan_count += 1
		loop_end_time = datetime.now()
		loop_time = (loop_end_time - loop_start_time).total_seconds()
	
		# Adjust the sleep time to aceive the target loop time and apply
		# with a slow acting correction added in to gradually improve accuracy
		sleep_time = config.scan_delay - loop_time - (correction/1000)
		if sleep_time < 0:
			sleep_time = 0
			print("program taking longer than config_scan_delay")
			print("Delay of only " + str(config.scan_delay) + " is too fast for accurate loop time adjustment")
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
		last_end = end_time
		end_time = datetime.now()
		last_total = (end_time - last_end).total_seconds()
		error = 1000*(last_total - config.scan_delay)
		correction = correction + (0.1*error)
	except KeyboardInterrupt:
		print(".........Ctrl+C pressed...")
		sys_exit()
