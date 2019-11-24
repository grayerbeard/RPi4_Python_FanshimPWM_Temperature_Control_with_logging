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

class class_control:  # for calc of freq and speed
	def __init__(self, config):
		self.config = config
		self.freq = config.min_freq
		self.speed = 0
		self.fan_on = False 

	def calc(self,temp):
		# Following gives 0 to 1 over range min_temp to max_temp
		self.throttle = 100*(temp - self.config.min_temp)/(self.config.max_temp - self.config.min_temp)
		if self.throttle < 0 :
			# Fan Off
			self.freq = self.config.min_freq
			self.speed = 0
			self.throttle = 0
			self.fan_on = False 
		elif self.throttle > 100 :
			# Fan at Max
			self.freq = self.config.max_freq
			self.speed = self.config.max_speed
			self.throttle  = 100
			self.fan_on = True 
		else:	
			# Fan "Throttled" between Min_speed and max_speed
			# Simarly for frequency
			self.freq = (self.throttle*(self.config.max_freq - self.config.min_freq)/100) + self.config.min_freq
			self.speed = (self.throttle*(self.config.max_speed - self.config.min_speed)/100) + self.config.min_speed
			self.fan_on = True 
		
