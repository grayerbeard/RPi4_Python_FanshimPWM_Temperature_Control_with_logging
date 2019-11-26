# R Pi 4 Python Fanshim PWM_Temperature Control with logging  BRANCH: Just PWM Fanshim

## Get code

To install the code that is controlling the fan on my R Pi 4 and producing the data below enter this command in the terminal:

'''
git clone https\://github\.com/grayerbeard/RPi4_Python_FanshimPWM_Temperature_Control_with_logging\.git -b pwm_fanshim --single-branch /home/pi/fanshim/
'''

That will create the folder "fanshim" (dont create it before) and install the code as a local git repository by extracting just this branch.

## Install Tmux

Then install "TMUX" using

sudo apt-get install tmux

(For info about tmux commands etc see mux-terminal-multiplexer-for-raspberry-pi or I prefer danielmiessler.com/study/tmux or many otherers if you google "tmux tutorial")

## Install Stress Testing

Then install the stress testing using the instructions at core-electronics.com.au/tutorials/stress-testing-your-raspberry-pi.html

(I have set up a bash command tmux_stress.sh to run the stress test see below)

## Edit rc.local to Start Code Automatically at Start Up

Then edit "/etc/rc.local" using the command

sudo nano /etc/rc.local

and add

sudo -u pi bash /home/pi/fanshim/tmux_start.sh &

## If want to use FTP to Send Files Edit the FTP_Creds File

To use FTP to a website edit "ftp_creds PATTERN.csv" and put it in a location that is matched by the location in config.cfg. (By default that is "/home/pi/ftp_creds/ftp_creds.csv")

If there is no file matching then FTP is not attempted. If the credentials are not right then FTP attempts will time out after the period set in the config.cfg file.

Similarly if the directory "/var/www/html/" does not exist because web server is not set up the copy of files there will simply fail.

(You can set up server with"sudo apt install nginx" then "sudo chown -R pi /var/www/html/". )

## Testing

Then go to that "fanshim" folder to start testing

Type

python3 fanshim.py

to check code working

then enter

./tmux_stress.sh

To do a stress test.

## Tweaking

Then you can try editing the parametsr in config.cfg to see if you get get the control more to your liking.

Then do a reboot and check the code runs automatically at start up.

## Checking up on Running Code

To check after start up to see if its still running enter

tmux ls

it should show fanshim is running.

or open the html file

fanshim_log.html

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

via the link at the top of the html file

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

## GitHub

Note that this is a branch of a github directory where I am developing variations of this sort of control function for cooling and heating with logging and remote monitoring.  An earlier version ran a heating with fan heaters in a community workshop for over two years.  e.g. room heating, sauna stove, central heating monitoring etc.  
A few weeks ago I decided to start getting the code a bit more proffessional looking and use github so I restarted by building up all the classes one at a time and improving them by gradually adding more applications with the aim of making sure code is reusable in the usual aim of good "Software Engineering" principals that I first studied around 35 years ago!.

I make frequest use of www.dataplicity.com to sort out issues remotely.  Great fun when someone is visiting the house and they want the Sauna Stove at a warmer temperature and I am in anouther country.  Or the Community Building workshop needs heating at a different time and I am away on holiday.   see other articles at https://www.smalle.uk/r-pi-4-blog.
Then using dataplicity to open a terminal on your R Pi one can use the tmux commands outlined above to take a look at what the code is doing.  Use GitHub to edit the code (once its in your own repository) and use "git pull" to put any revised code into the R Pi even when you are far from home.   Note that its no good setting code running using SSH or dataplicity as then when the link is closed the code stops.  That is the joy of using tmux.

## Help

Any issues email me at feedback@smalle.uk or look on https://www.smalle.uk/r-pi-4-blog
