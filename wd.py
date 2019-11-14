#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   for use with Python 3

#	wd_module_036.py
 
#	This program is free software; you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation; either version 2 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNimport sys, getoptESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#  
#	You should have received a copy of the GNU General Public License
#	along with this program; if not, write to the Free Software
#	Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#	MA 02110-1301, USA.

from csv import DictReader as csv_DictReader
from csv import DictWriter as csv_DictWriter

class class_wd: #For sending status etc to Watchdog
	def __init__(self,wd_filename):
		self.fields = ['count','status']
		self.filename = wd_filename + ".csv"
		self.count = "None"
		self.status = "Very Unknown"

	def put_wd(self,count,status):
		with open(self.filename, 'wt') as wdfile:
			writer = csv_DictWriter(wdfile, fieldnames = self.fields)
			writer.writeheader()
			writer.writerow({'count': count,'status': status,})

	def get_wd(self):
		with open(self.filename) as csvfile:
			d_file = csv_DictReader(csvfile)
			for row in d_file:
				self.count = str(row['count'])
				self.status = str(row['status'])
				print("Received From : ",self.filename,self.count)

