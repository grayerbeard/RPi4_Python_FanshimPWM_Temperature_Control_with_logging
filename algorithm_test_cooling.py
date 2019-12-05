#!/usr/bin/env python3
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

# title           :algorithm.py
# description     :pwm control for R Pi Cooling Fan
# author          :David Torrens
# start date      :2019 11 20
# version         :0.1
# python_version  :3

# Notes
# a python3 script to calc output parameters based on configuration and current temperature
# where the objective is limiting maximum temperature rather than maintaining a target temperature
# Slight improvement on method used for last few months put into separate class
#https://en.m.wikipedia.org/wiki/Algorithm
#https://github.com/ivmech/ivPID
#first writen November 2019

from utility import do_command

class class_control:  # for calc of freq and speed
	def __init__(self, config):
		self.config = config
		self.freq = config.min_freq
		self.stress_count = 3
		self.stress_flag = False
		self.speed = 0
		self.fan_on = False
		self.do_first_test_flag = True
		self.test_count = 20
		self.test_load_max = config.test_load_max
		self.test_values = [self.config.min_speed] * (self.test_count + 1)
		for ind_test_values in range(self.test_count,0,-1):
			self.test_values[ind_test_values] = ((ind_test_values/self.test_count)*(100 - self.config.min_speed)) + self.config.min_speed
		print("self.test_values : ",self.test_values)

	def calc(self,temp,cpu_load):
		# Following gives 0 to 1 over range min_temp to max_temp
		self.throttle = 100*(temp - self.config.min_temp)/(self.config.max_temp - self.config.min_temp)
		
		if (self.throttle > 50) and (cpu_load == 100) and self.do_first_test_flag and (self.test_count >= 0):
			#warm enough so stop stress test
			if self.stress_flag:
				print("Stop stress test")
				do_command("tmux_stop_stress.sh")
				self.stress_flag = False
			self.stress_count = 3
		if self.stress_count > 0:
			self.stress_count -= 1
			print("Doing Count Down, self.stress_count : ",self.stress_count)
		elif (self.stress_count <= 0):
			if not(self.stress_flag):
				print("initiate stress test")
				do_command("tmux_stress.sh")
				self.stress_flag = True
			self.stress_count = 0
		if (self.throttle > 50) and (self.test_count >= 0):# and (cpu_load < self.test_load_max):
			self.speed = self.test_values[self.test_count]
			self.test_count -=1
			print("Tests Left to do is : ",self.test_count)
			self.fan_on = True
			self.throttle  = 101
			self.freq = self.config.max_freq
		elif self.throttle < 0 :
			# Fan Off
			self.freq = self.config.min_freq
			self.speed = 0
			self.throttle = 0
			self.fan_on = False 
		elif self.throttle > 100 and (self.test_count <= 0):
			# Fan at Max
			self.freq = self.config.max_freq
			self.speed = self.config.max_speed
			self.throttle  = 100
			self.fan_on = True 
		elif (self.test_count <= 0):
			# Fan "Throttled" between Min_speed and max_speed
			# Simarly for frequency
			self.freq = (self.throttle*(self.config.max_freq - self.config.min_freq)/100) + self.config.min_freq
			self.speed = (self.throttle*(self.config.max_speed - self.config.min_speed)/100) + self.config.min_speed
			self.fan_on = True
		elif temp > self.config.max_temp:
			self.freq = self.config.min_freq
			self.speed = self.config.min_speed
			self.throttle = 102
			self.fan_on = True
		else:
			self.freq = self.config.min_freq
			self.speed = 0
			self.throttle = 0
			self.fan_on = False
		if self.do_first_test_flag and (self.test_count <= 0):
			self.test_count = 20
			self.do_first_test_flag = False
			print("Starting second test")
			self.throttle = 104
