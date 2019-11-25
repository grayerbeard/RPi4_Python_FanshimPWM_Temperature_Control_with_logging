# R Pi 4 Python Fanshim PWM_Temperature Control with logging  BRANCH: Just PWM Fanshim

To install the code that is controlling the fan on my R Pi 4 and producing the data below enter this command in the terminal:

git clone https://github.com/grayerbeard/RPi4_Python_FanshimPWM_Temperature_Control_with_logging.git -b pwm_fanshim --single-branch /home/pi/fanshim/

That will create the folder "fanshim" (dont create it before) and install the code.

Then install "TMUX" using

sudo apt-get install tmux

(For info about tmux commands etc see mux-terminal-multiplexer-for-raspberry-pi or I prefer danielmiessler.com/study/tmux or many otherers if you google "tmux tutorial")

Then install the stress testing using the instructions at core-electronics.com.au/tutorials/stress-testing-your-raspberry-pi.html

(I have set up a bash command tmux_stress.sh to run the stress test see below)

Then edit "/etc/rc.local" using the command

sudo nano /etc/rc.local

and add

sudo -u pi bash /home/pi/fanshim/tmux_start.sh &

To use FTP to a website edit "ftp_creds PATTERN.csv" and put it in a location that is matched by the location in config.cfg. (By default that is "/home/pi/ftp_creds/ftp_creds.csv")

If there is no file matching then FTP is not attempted. If the credentials are not right then FTP attempts will time out after the period set in the config.cfg file.

Similarly if the directory "/var/www/html/" does not exist because web server is not set up the copy of files there will simply fail.

(You can set up server with"sudo apt install nginx" then "sudo chown -R pi /var/www/html/". )

Then go to that "fanshim" folder to start testing

Type

python3 fanshim.py 

to check code working

then enter

./tmux_stress.sh

To do a stress test.

Then you can try editing the parametsr in config.cfg to see if you get get the control more to your liking.

Then do a reboot and check the code runs automatically at start up.

To check after start up enter

tmux ls

it should show fanshim is running.

to look at what is happening

or open the html file in the fanshim directory

fanshim_log.html

or the log file iin /home/pi/fanshim/log

or from any other device on your local network using your R Pi IP e.g. http://192.168.250.100/fanshim_log.html

or the command to watch on your terminal

tmux a -t fanshim

to exit enter

"ctrl-b" then "d".

My dvelopment repository on GitHub at github.com/grayerbeard/RPi4_Python_FanshimPWM_Temperature_Control_with_logging with just the fanshim code in the "pwm_fanshim branch"

Any issues email me at feedback@smalle.uk or look on https://www.smalle.uk/r-pi-4-blog
