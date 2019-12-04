# R Pi 4 Python Fanshim PWM_Temperature Control with logging

## Get code

To install this code that was controlling the fan on my R Pi 4 on December 3rd 2019 use the usual green "Clone or Download" button above.

This code was copied in from the [pwm_fanshim](https://github.com/grayerbeard/RPi4_Python_FanshimPWM_Temperature_Control_with_logging/tree/pwm_fanshim) branch of my [RPi4_Python_FanshimPWM_Temperature_Control_with_logging](https://github.com/grayerbeard/RPi4_Python_FanshimPWM_Temperature_Control_with_logging) repository on December 3rd 2019 where I will continue to develope the code further.

This is a stable version that had been running for several days.  I have included a large log file from the R Pi 4  running continuously for several days and some screenshots of the HTML logging file.

I would suggest putting the files in a directory /home/pi/fanshim and then following the instructions below.

The use of FTP to a remote site is optional and if no FTP Credential file is set up will be bypassed with data just logged locally.  The point of this long term logging is that stress tests does not tell you what is happening under normal use when ideally you want a reasonable temperature maintained with minimal use of the fan.

## Issues

* After several days the csv file gets quite big and causes code to run slower.
* Related to above the use of FTP starts to cause problems with the time taken to upload files.

## Proposed solution I will work on in next months.

* Make the FTP a separate tmux triggered process
* Start a new log file periodically
* Reduce the amount of data sent to log file when R Pi is "idle" and fan not in use.

## Install Tmux

You will need to install "TMUX" to start the code in the way recommended using

'''
sudo apt-get install tmux
'''

(For info about tmux commands etc see
'''
[tmux-terminal-multiplexer-for-raspberry-pi](https://iotpoint.wordpress.com/2016/11/15/tmux-terminal-multiplexer-for-raspberry-pi/) 
or I prefer
[Daniel Miessler tmux](https://danielmiessler.com/study/tmux/) and best of all [Dataplicity.com docs Run Your Scripts In Background](https://docs.dataplicity.com/docs/run-your-scripts-in-background)
'''
or many other places if you google for  "tmux tutorial".

NOTE: If you download the files and install using the Zip file you may need to change the permissions on the tmux ..sh files to make them executable. 

## Install Stress Testing

Then install the stress testing using the instructions at 
'''
[Stress Testing Your Raspberry Pi](https://core-electronics.com.au/tutorials/stress-testing-your-raspberry-pi.html)
'''

(I have set up a bash command tmux_stress.sh to run the stress test see below)

## Edit rc.local to Start Code Automatically at Start Up

Then edit "/etc/rc.local" using the command

'''
sudo nano /etc/rc.local
'''

and add

'''
sudo -u pi bash /home/pi/fanshim/tmux_start.sh &
'''

## If want to use FTP to Send Files Edit the FTP_Creds File

To use FTP to a website edit "ftp_creds PATTERN.csv" and put it in a location that is matched by the location in config.cfg. (By default that is "/home/pi/ftp_creds/ftp_creds.csv")

If there is no file matching then FTP is not attempted. If the credentials are not right then FTP attempts will time out after the period set in the config.cfg file.

Similarly, if the directory "/var/www/html/" does not exist because web server is not set up the copy of files there will simply fail.

(You can set up server with "sudo apt install nginx" then "sudo chown -R pi /var/www/html/" so the folder is writeable by the code. )

## Testing

Go to that "fanshim" folder to start testing (cd /home/pi/fanshim)

Type

'''
python3 fanshim.py
'''

to check code working

then enter this to run stress test

'''
./tmux_stress.sh
'''

(Note the full stop at start of above)

Then you can check the normal way of starting with this command (which will be called automatically at start up if you have edited rc.local)

'''
./tmux_start.sh
'''

(Note the full stop at start of above)

Then you can check running with 

'''
tmux ls
'''

## Tweaking

Then you can try editing the parameters in config.cfg to see if you get the control more to your liking.

Then do a reboot and check the code runs automatically at start up.

## Checking up on Running Code

To check after start up to see if its still running enter

'''
tmux ls
'''

it should show fanshim is running.

or open the html file with your browser

'''
/home/pi/fanshim/fanshim_log.html
'''

it should be in both of these locations (as well as copied to website if FTP was set up) : 
"/home/pi/fanshim"  and "/var/www/html" ,

The file at "/var/www/html" can be opened with a browser from  any device on your local network using , from any device using the RPi's IP address e.g. 192.168.0.101/fanshim_log.html, (use "ifconfig" at the terminal to get the IP address).

On my web site I have in the past used an iframe to show the "live" file in a Joomla Article; this is the html used:

'''
\<p\>\<iframe src="https\:\/\/www\.ftp4rpi\.smalle\.uk/house/fanshim_log\.html" frameborder="0" width="1100" height="1000" style="float: left;"\>\</iframe\>\</p\>
'''

The HTML file only shows recent data but all data since start up is in a csv log file you can open with a spreadsheet they are in "/home/pi/fanshim/log" and "/var/www/html/log".

There is a link at the top of the html file that link to the CSV log file. The csv files are retained until deleted whereas html files get overwritten; so, the csv file is the best way to review long term behaviour.

You can us this command to open a "tmux window" to observe the code's print out

'''
tmux a -t fanshim
'''

to exit that tmux window enter

'''
"ctrl-b" then "d"
'''
## All the ways to stop the python3 code
* In tmux window enter "ctrl C", 
* in fanshim directory enter "./tmux_stop.sh" (will also stop a running stress test) or 
* enter "tmux kill-session -t fanshim"

## "What Else you doing? and About using GitHub with Dataplicity 

### What else I am up to?
This pwm_fanshim branch is from my github directory where I am developing variations of this sort of control function for cooling and heating with logging and remote monitoring.  This branch only has what is needed for PWM of the fanshim.

I had used the earlier version developed without GitHub (silly me!) for controlling fan heaters using TPLink Smartplugs with remote monitoring of a  community workshop for over two years.  I also had a version for PWM control of a Sauna Heater. Soon I will redo these using the same background classes.

### Getting Tidier with GitHub

A few weeks ago I decided to start getting the code a bit more professional looking and use github.  So I restarted by redoing the background classes and testing using "test_text_buffer.py".  Then this branch to control the fan came next. In next months will get the Sauna and House Heating versions working again.

### How I work

I make frequent use of [dataplicity.com](https://www.dataplicity.com) to sort out issues remotely.  Great fun when someone is visiting the house and they wanted the Sauna Stove at a warmer temperature and I am in another country.  Or the Community Building workshop needed heating at a different time and I am away on holiday.   See other articles at [www.smalle.uk/r-pi-4-blog](https://www.smalle.uk/r-pi-4-blog) for how I set that up.

I use dataplicity to open a terminal on my R Pi so can then use the tmux commands outlined above to take a look at what the code is doing. I have tried other methods but I find it best to usually use GitHub to edit the code (which you could do once its in your own repository) and I then use "git pull" to put any revised code from GitHub into the R Pi, this can then work even when you are far from home.  Only occasionally do I use geany locally to edit and then "git push" to upload the result because I find the work flow often gets confused.

### A warning when using Datplicity or SSH

Note that its no good setting code running using SSH or dataplicity terminal direct as then when the link is closed the code stops.  That is the joy of using tmux, a tmux session carries on once you exit with "ctrl b" "d".  For more info see [docs.dataplicity.com/docs](https://docs.dataplicity.com/docs)

## Help

Any issues email me at [feedback@smalle.uk](mailto:feedback@smalle.uk) or look on [www.smalle.uk/r-pi-4-blog](https://www.smalle.uk/r-pi-4-blog)
