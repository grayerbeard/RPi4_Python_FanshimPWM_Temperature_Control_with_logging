# Standard library imports
from subprocess import call as subprocess_call
from utility_036 import fileexists
from time import sleep as time_sleep
from datetime import datetime

mount_try = 1
mounted = False
start_time = datetime.now()
when = datetime.now()

while (mount_try < 30) and not(mounted):
	try:
		mounted = fileexists("/home/pi/mycloud/Tests/test2.zip")
		if not(mounted):
			print("Needs mounting this is try number: ", mount_try)
			subprocess_call(["sudo", "mount", "-a"])
			mount_try += 1
		mounted = fileexists("/home/pi/mycloud/Tests/test2.zip")
		if mounted:
			when = datetime.now()
			when = round((when - start_time).total_seconds(),2)
			print("Success at :",when, " secs from start")
	except:
		print("Count: ", count,"  error lines 12 to 19")
	time_sleep(1)


while True:
	time_sleep(20000)
