#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
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

# title           :utility.py
# description     :pwm control for R Pi Cooling Fan
# author          :David Torrens
# start date      :2019 11 20
# version         :0.1
# python_version  :3

# Standard library imports
from csv import DictReader as csv_DictReader
from datetime import datetime
from ftplib import FTP

# Third party imports
# None

# Local application imports
# None

# Standard or Installed Modules
# none

def in_GUI_mode():
	mode = 1
	try:
		if sys.stdin.isatty():
			mode = 0
	except AttributeError:  # stdin is NoneType if not in terminal mode
		pass
	if mode == 0:
		#in terminal mode
		return(False)
	else:
		#in gui mode ...
		return(True)

def list_files(path,exclude):
	# List all files in path "path" bu exclude items matching "exclude"
	# Result is returned as a list
	here = "list_files"
	emptylist= []
	files = []
	try:
		seen_files = listdir(path)
		pr(here,"Number of file found : ", str(len(seen_files)))
		for ind in range(0,len(seen_files)):
			if (seen_files[ind] == exclude) or (seen_files[ind][:2] == "00"):
				pr(here,"seen_file[" + str(ind)+"] is not OK : ",seen_files[ind])
			else:	
				pr(here,"seen_file[" + str(ind)+"] is OK : ",seen_files[ind])
				files.append(seen_files[ind])
		return(files)
	except:
		status_bffr.pr(True,0,"Error in subroutine list_files")
		return(emptylist)

def pr(flag,where,message,var_val):
	# routine for debugging that prints message then a variables value
	if flag:
		if str(var_val) == "":
			print("debug: ", where , " : ", message, "Val Empty")
		else:
			print("debug: ", where , " : ", message, str(var_val))
	return

def fileexists(filename):
	#This checks for file but does not detect disconnected sensor
	try:
			with open(filename): pass
	except IOError:
			return False 
	return True

def show_html(html_filename):
	# open a file in the default program
	here = "show_html"
	pr(here, "Show file at this url : ", " file://" + html_filename)
	url = "file://" + html_filename
	webbrowser.open(url,new=2) # new=2 signals new tab
	
def make_time_text(time_value):
	#make a time stamp in format mm:dd hr:mn:sc
	return(str(time_value.month).zfill(2) + "_" + str(time_value.day).zfill(2) + "__"
	  + str(time_value.hour).zfill(2) + "_" + str(time_value.minute).zfill(2) +"_"
	  + str(time_value.second).zfill(2))


def send_by_ftp(dbug_send_ftp,ftp_cred,send_filename, save_as_filename, ftp_remote_dir,ftp_timeout):
	here = "send_by_ftp"
	result = ["FTP attempt for :" + send_filename]
	
	# Use Following two lines for debug to check parameters received by send_by_ftp
	#print("send_by_ftp: dbug_send_ftp: ",dbug_send_ftp," ftp_cred: ", ftp_cred, \
	#	" send_filename: ",send_filename, "save_as_filename: ",save_as_filename, "ftp_remote_dir: ",ftp_remote_dir)


	try:
		with open(ftp_cred, 'r') as csvfile:
			cred_file = csv_DictReader(csvfile)
			ind = 0
			for row in cred_file:
				if ind == 0:
					ftp_user = row['user']
					pr(dbug_send_ftp,here ,"ftpuser : ",ftp_user)
					ftp_password = row['password']
					pr(dbug_send_ftp,here,"ftp password : ", ftp_password)
					file_2_send = str(send_filename)
					ftp_directory = str(row['directory']) + "/" + ftp_remote_dir
					pr(dbug_send_ftp,here, "ftp directory : ",ftp_directory)
					ftp_site =  str(row['site'])
					pr(dbug_send_ftp,here, "ftp site : ", ftp_site)
				else:
					result.append("Error more than one line in FTP creds file")
					return(result)
				ind += 1
		ftp = FTP()
		debug_level = 1
		if dbug_send_ftp:
			ftp.set_debuglevel(debug_level)
			print("--------FTP Debug on------------ftp_timeout : ",ftp_timeout,"degug_level : ",debug_level)
		pr(dbug_send_ftp,here,"Will try to connect to : ", ftp_site)
		pr(dbug_send_ftp,here,"WTimeout is set to : ",ftp_timeout)
		ftp.connect(ftp_site, 21,timeout=ftp_timeout)
		pr(dbug_send_ftp,here, "logging in here is ftp welcome message : ",ftp.getwelcome())
		ftp.login(user=ftp_user,passwd=ftp_password)
		pr(dbug_send_ftp,here, "logged in to : ",ftp_site)
		ftp.cwd(ftp_directory)
		pr(dbug_send_ftp,here, "directory changed to : ", ftp_directory)  
	
		sendfile  = open(send_filename,'rb')
		result.append("Will try to send : " + send_filename + " : as : "
		             + save_as_filename + " to : " +  ftp_site + "/" + ftp_directory)
		ftp.storbinary('STOR ' + save_as_filename,sendfile)
		sendfile.close()
		
		ftp.quit()
		pr(dbug_send_ftp,here, "ftp quitedfrom : ", ftp_site)
		pr(dbug_send_ftp,here,"Done FTP",save_as_filename)
		return(result)
	except:
		pr(dbug_send_ftp,here,"Failed FTP",save_as_filename)
		result.append("Error Trying To Send " + send_filename + " file by FTP")
		print("Error Trying To Send " + send_filename + " file by FTP", "Try setting dbug flag to investigate")
	return(result)

