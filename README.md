# R Pi 4 Python Fanshim PWM_Temperature Control with logging  BRANCH: Just PWM Fanshim

## Get code

To install the code that is controlling the fan on my R Pi 4 and producing the data below (at the bottom of the page) via this link to [the html file uploaded to my website](https://www.ftp4rpi.smalle.uk/house/fanshim_log.html) enter this command in the terminal:

'''
git clone https\://github\.com/grayerbeard/RPi4_Python_FanshimPWM_Temperature_Control_with_logging\.git -b pwm_fanshim --single-branch /home/pi/fanshim/
'''

That will create the folder "fanshim" (dont create it before) and install the code as a local git repository by extracting just this branch.

The use of FTP to a remote site is optional and if not set up will be bypassed with data just logged locally.  The point of this long term logging is that stress tests dont tell you what is happening under normal use when ideally you want a reasonable temperature maintained with minimal use of the fan.

## Install Tmux

Then install "TMUX" using

'''
sudo apt-get install tmux
'''

(For info about tmux commands etc see
'''
[tmux-terminal-multiplexer-for-raspberry-pi](https://iotpoint.wordpress.com/2016/11/15/tmux-terminal-multiplexer-for-raspberry-pi/) 
or I prefer
[Daniel Miessler tmux](https://danielmiessler.com/study/tmux/) and best of all [Dataplicity.com docs Run Your Scripts In Background](https://docs.dataplicity.com/docs/run-your-scripts-in-background)
'''
or many otherer places if you google for  "tmux tutorial"

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

Similarly if the directory "/var/www/html/" does not exist because web server is not set up the copy of files there will simply fail.

(You can set up server with"sudo apt install nginx" then "sudo chown -R pi /var/www/html/". )

## Testing

Then go to that "fanshim" folder to start testing

Type

'''
python3 fanshim.py
'''

to check code working

then enter

'''
./tmux_stress.sh
'''

(Note the full stop at start of above)

To do a stress test.

Then you can check the normal way of starting with 

'''
./tmux_start.sh
'''

(Note the full stop at start of above)

Then you can check running with 

'''
tmux ls
'''

## Tweaking

Then you can try editing the parametsr in config.cfg to see if you get get the control more to your liking.

Then do a reboot and check the code runs automatically at start up.

## Checking up on Running Code

To check after start up to see if its still running enter

'''
tmux ls
'''

it should show fanshim is running.

or open the html file

'''
fanshim_log.html
'''

in either of these locations : 
/home/pi/fanshim,
/var/www/html ,
from  your network , from any device using a browser and the R Pis IP addressvso e.g. 192.168.0.101/fanshim_log.html,
remote web site as shown on this page where (I use an iframe), this is the html used at the bottom of this page which is created using:

'''
\<p\>\<iframe src="https\:\/\/www\.ftp4rpi\.smalle\.uk/house/fanshim_log\.html" frameborder="0" width="1100" height="1000" style="float: left;"\>\</iframe\>\</p\>
'''

or open the csv log file in 

'''
/home/pi/fanshim/log or  
/var/www/html/log or 
'''

via the link at the top of the html file that link to the CSV log file (csv files are retained until deleted whereas html files get overwritten; so the csv file is the best way to review long term behavior.

or this command to open a "tmux window" to observe the code's print out

'''
tmux a -t fanshim
'''

to exit that tmux window enter

'''
"ctrl-b" then "d"
'''

## To Stop

In tmux window enter "ctrl C", in fanshim directory enter "./tmux_stop.sh", or enter "tmux kill-session -t fanshim"

## About using GitHub with Dataplicity 

Note that this is a branch of a github directory where I am developing variations of this sort of control function for cooling and heating with logging and remote monitoring, but this branch only has what is needed for fan control with logging.
I have used the earlier version developed without GitHub (silly me) for heating with remote monitoring of a  community workshop for over two yaers. 
A few weeks ago I decided to start getting the code a bit more proffessional looking and use github so I restarted by building up all the classes one at a time and improving them by gradually adding more applications with the aim of making sure code is reusable in the usual maner of good "Software Engineering" principals that I first studied around 35 years ago in the days when one did the required exercises by visiting somewhere where you could enter code on a teletype.

I make frequest use of [dataplicity.com](https://www.dataplicity.com) to sort out issues remotely.  Great fun when someone is visiting the house and they want the Sauna Stove at a warmer temperature and I am in anouther country.  Or the Community Building workshop needs heating at a different time and I am away on holiday.   See other articles at [www.smalle.uk/r-pi-4-blog](https://www.smalle.uk/r-pi-4-blog) for how I set that up.

I use dataplicity to open a terminal on my R Pi so can then use the tmux commands outlined above to take a look at what the code is doing. I have tried othet methods but I find it best to use GitHub to edit the code (which you could do once its in your own repository) and I then use "git pull" to put any revised code from GitHub into the R Pi, this can then work even when you are far from home.
Note that its no good setting code running using SSH or dataplicity terminal direct as then when the link is closed the code stops.  That is the joy of using tmux.  For more info see [docs.dataplicity.com/docs](https://docs.dataplicity.com/docs)

## Help

Any issues email me at [feedback@smalle.uk](mailto:feedback@smalle.uk) or look on [www.smalle.uk/r-pi-4-blog](https://www.smalle.uk/r-pi-4-blog)
