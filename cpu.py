#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# This file is part of pwm_fanshim.
# Copyright (C) 2015 Ivmech Mechatronics Ltd. <bilgi@ivmech.com>
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# title           :cpu.py
# description     :pwm control for R Pi Cooling Fan
# author          :David Torrens
# start date      :2019 11 20
# version         :0.1
# python_version  :3

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
		self.cpu_mem = psutil.virtual_memory().percent
		self.cpu_disk = psutil.disk_usage('/').percent
		self.cpu_freq = psutil.cpu_freq()

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
