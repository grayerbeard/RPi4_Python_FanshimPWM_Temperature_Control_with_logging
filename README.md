# R Pi 4 Python Fanshim PWM_Temperature Control with logging  BRANCH: Just PWM Fanshim

R Pi 4 with Fanshim Cooling controlled with PWM.  Nice quiet Fan Cooling normally never runs fan at more than 75% speed which is very much quieter.

Everying in the Branch Tested for a prolonged period but this brandch only set up on November 24th 2019 so it will take a day or two to be sure the branch is working OK.
Note that the code is started with the ./tmux_start.sh command from the fanshim directory.   
This can be triggered automatically on startup with the following added to  /etc/rc.local

sudo -u pi bash /home/pi/fanshim/tmux_start.sh &

Then if you want to see what is happening type this in the termional

tmux a -t fanshim

Parameters used are all in a config,cfg file so you can mess with them easily using a text editor; however the values chosen are the result of many hours of fiddling so the only reason to change would be if need to increse cooling when overclocking or other such exotic stuff.
