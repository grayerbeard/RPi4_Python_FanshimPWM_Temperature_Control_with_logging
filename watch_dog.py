# Standard library imports
from subprocess import call as subprocess_call
from time import sleep as time_sleep
from datetime import datetime
from os import getpid
from os import path
import sys
import subprocess

# Third party imports
# None

# Local application imports
from config import class_config
from text_bffr import class_text_bffr
from wd import class_wd

def do_command(cmnd):
	subprocess_call(['./' + cmnd])
	return []

wd1 = class_wd("temp_control_wd")
wd2 = class_wd("cpu_wd")
config = class_config()

config.prog_name = str(sys.argv[0][:-3])
print("Program Name is : ",config.prog_name)
prg_version = config.prog_name[-3:]
print("So Version taken as : ",prg_version)

my_pid = getpid()

print("start ver " + prg_version + "   My PID (Process ID) is : " + str(my_pid))

config.prog_path = path.dirname(path.realpath(__file__)) + "/"
config.config_filename = config.prog_path +  "config_" + prg_version + ".cfg"
 
print( "Just set config file to : ", config.config_filename)

config.set_filename(config.config_filename)
config.read_file()
sleep_time = 2 + (config.scan_delay)/5
print("sleeptime is : ",sleep_time)

wd_bffr_width = 5

wd_bffr = class_text_bffr(200,wd_bffr_width,"wd",config)
wd_bffr.setup_log(config)
wd_bffr.set_bffr_heading("WD Count")
wd_bffr.set_bffr_heading("Msg")
wd_bffr.set_bffr_heading("Count_1")
wd_bffr.set_bffr_heading("MCount2")
wd_bffr.set_bffr_filenames("wd_log.html",config.prog_path + "wd_log.html",config.local_dir_www + "wd_log.html",config.ftp_creds_filename)
wd_bffr_values = [""] * (wd_bffr_width-1)
last_fail = "None"
wd_status = "unknown"
wd_prog_count = 0
last_count_rcvd_1 = 0
last_count_rcvd_2 = 0
max_fail_1 = 0
max_fail_2 = 0
wd_inc_1 = 0
wd_inc_2 = 0
repeat_fail_1 = 0
repeat_fail_2 = 0
last_count_rcvd_1 = 0
last_count_rcvd_2 = 0

ind = 0

while True: 

	#Following two lines can be used to test code
	#wd.put_wd(ind,"ok" + str(2*ind))
	#ind += 1

	try:
		wd1.get_wd()
		repeat_fail_1 = 0
	except:
		repeat_fail_1 += 1
		if repeat_fail_1 > max_fail_1:
			max_fail_1 = repeat_fail_1
		print("No WD File fail_count: ",repeat_fail_1," max repeat fail: ",max_fail_1 )
	try:
		wd2.get_wd()
		repeat_fail_2 = 0
	except:
		repeat_fail_2 += 1
		if repeat_fail_2 > max_fail_2:
			max_fail_2 = repeat_fail_2
		print("No WD File - fail_count: ",repeat_fail_1," max repeat fail: ",max_fail_2 )

	if wd1.count == last_count_rcvd_1:
		wd_inc_1 += 1
	else:
		wd_inc_1 = 0
	last_count_rcvd_1 = wd1.count

	if wd2.count == last_count_rcvd_2:
		wd_inc_2 += 1
	else:
		wd_inc_2 = 0
	last_count_rcvd_2 = wd2.count
	
	wd_bffr_values[1] = ""

	if wd_inc_1 > 10 :
		wd_bffr_values[1] += " wd_1 Fail "
		do_command("tmux_restart_1.sh")
		wd_bffr_values[2] = str(last_count_rcvd_1) + "/" + str(wd_inc_1)
		wd_inc_1 = 0
	else:
		wd_bffr_values[2] = str(last_count_rcvd_1) + "/" +str(wd_inc_1)
	if wd_inc_2 > 10 :
		wd_bffr_values[1] += " wd_2 Fail "
		do_command("tmux_restart_2.sh")
		wd_bffr_values[3] = str(last_count_rcvd_2) + "/" +str(wd_inc_2)
		wd_inc_2 = 0
	else:
		wd_bffr_values[3] = str(last_count_rcvd_2) + "/" +str(wd_inc_2)

	wd_bffr_values[0] = str(wd_prog_count)
	wd_bffr.pr(True,0, wd_bffr_values)
	time_sleep(sleep_time)
