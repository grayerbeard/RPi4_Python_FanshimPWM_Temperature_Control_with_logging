#!/usr/bin/env python3

#calgorithm_o1.py a python3 script to return control output parameters
#first writen November 2019

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



from gpiozero import CPUTemperature
import RPi.GPIO as GPIO
import psutil
import datetime
import plasma
import colorsys

class class_cpu:  # For monitoring R Pi 4 Cpu 
	def __init__(self):
		self.get_cpu_temp = CPUTemperature() 
		self.temp = float(self.get_cpu_temp.temperature)
		self.cpu_load = psutil.cpu_percent(interval=None,percpu=False) # gives average since last call all cpus.
		self.total_for_average_power = self.cpu_load
		self.average_load = self.temp
		self.averageing_count = 1
		self.cpu_mem = psutil.virtual_memory().percent
		self.cpu_disk = psutil.disk_usage('/').percent                 
		self.last_call = datetime.datetime.now()
		self.this_call = datetime.datetime.now()
		self.since_last = 0.0
		self.cpu_freq = psutil.cpu_freq()
		self.pwm_speed  = 0
		self.pwm_freq = 2
		self.pwm_on_time = 100
		#self.pwm_count = 0
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(18, GPIO.OUT)
		self.pwm_out = GPIO.PWM(18,1)
		self.pwm_out.start(0)
		self.pwm_out.ChangeFrequency(self.pwm_freq)
		self.pwm_out.ChangeDutyCycle(self.pwm_speed)

	def set_pwm_control_fan(self,freq,speed):
		self.pwm_speed  = speed
		self.pwm_freq = freq

	def control_fan(self):
		self.pwm_out.ChangeFrequency(self.pwm_freq)
		self.pwm_out.ChangeDutyCycle(self.pwm_speed)

	def get_data(self):
		self.temp = float(self.get_cpu_temp.temperature)
		self.cpu_load = psutil.cpu_percent(interval=1)
		self.total_for_average_power += self.cpu_load
		self.averageing_count += 1
		self.cpu_mem = psutil.virtual_memory().percent
		self.cpu_disk = psutil.disk_usage('/').percent
		self.cpu_freq = psutil.cpu_freq()

	def calc_averages(self):
		self.average_load = round(self.total_for_average_power/self.averageing_count,2)
		self.averageing_count = 0
		self.total_for_average_power = 0

	def get_av_cpu_load_so_far(self):
		average_load_so_far = round(self.total_for_average_power/self.averageing_count,2)
		return ("Now Load : " + str(self.cpu_load) + "  With Average So far : " + str(average_load_so_far))

	def update_led_temperature(self,temp,min_temp,max_temp,brightness):
		temp = float(temp)
		temp -= max_temp
		temp /= float(min_temp - max_temp)
		temp = max(0, min(1, temp))
		temp = 1.0 - temp
		temp *= 120.0
		temp /= 360.0
		r, g, b = [int(c * 255.0) for c in colorsys.hsv_to_rgb(temp, 1.0, brightness / 255.0)]
		plasma.set_light(0, r, g, b)
plasma.show()



try_throttle_calc = 100 * (cpu.temp - config.min_temp)/(config.max_temp - config.min_temp)
		try_throttle_calc_smoothed = try_throttle_calc_smoothed + 0.1*(try_throttle_calc - try_throttle_calc_smoothed)
		change = cpu.temp - last_cpu_temp
		if change > 1.1:
			print("---------------- Big CTemp Increase : ",last_cpu_temp, " to ",cpu.temp, " so ", change)
		last_cpu_temp = cpu.temp
	
		# Check CPU temperature situation to use in below IF  statements
		# Display data occasionally
		c_or_1 = sub_count >= 0.998
		# Turn off Fan when on and below target range
		c_or_2 = (throttle > 0) and (cpu.temp<lower_min_temp)  # e.g. if using 61 to 69 then 57
		# Turn fan on when temperature increasing fast
		c_or_3 = (change > 2.1) and (cpu.temp > lower_mid_temp)# e.g. if using 61 to 69 then 63
		# Turn fan on when temperature approaching top of target range.
		c_or_4 = cpu.temp >= upper_mid_temp 				   # e.g. if using 61 to 69 then 67	
	
		if c_or_1 or c_or_2 or c_or_3 or c_or_4:
	
			buffer_increment_flag = True
	
			cpu.calc_averages()
	
			if cpu.temp >= config.max_temp:
				throttle = 100
			elif cpu.temp<= config.min_temp:
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
				freq = config.min_freq
			else:
				speed = config.min_speed + (throttle*(config.max_speed-config.min_speed)/100)
				freq = config.max_freq
	
			cpu.set_pwm_control_fan(freq,speed)
	
			cpu.update_led_temperature(cpu.temp,config.max_temp,config.min_temp,config.brightness)
	
			cpu_buffer.line_values[0] = str(round(config.scan_count + sub_count,3))
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
			sub_count = 0
		
		else:
			#Uncomment following Two lines to observe if curious
			#print(" Count : ",round(config.scan_count+sub_count,2),cpu.get_av_cpu_load_so_far(),"Temp : ",
			#	round(cpu.temp,2),"Throttle/smoothed : ",round(try_throttle_calc,2),"/",round(try_throttle_calc_smoothed,2)) 
			cpu_buffer.line_values[0] = str(round(config.scan_count + sub_count,3))
			
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
		error = 1000*(last_total - 5)
		correction = correction + (0.05*error)
		#print("Error : ",1000*(last_total - 5),correction)
	except KeyboardInterrupt:
		print(".........Ctrl+C pressed...")
		sys_exit()





