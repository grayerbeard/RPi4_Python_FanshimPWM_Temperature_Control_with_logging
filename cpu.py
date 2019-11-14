#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	cpu_037.py

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
