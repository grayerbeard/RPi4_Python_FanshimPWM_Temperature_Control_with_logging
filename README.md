# RPi4_Python_FanshimPWM_Temperature_Control_with_logging  BRANCH: Just Fanshim
R Pi 4 with Fanshim Cooling controlled with PWM

Everying in the Branch Tested for a prolonged period but this brandch only set up on November 24th 2019 so it will take a day or two to be sure the branch is working OK.
Note that the code is started with the ./tmux_start.sh command.   
This can be triggered automatically on startup with the following added to  /etc/rc.local

sudo -u pi bash /home/pi/fanshim/tmux_start.sh &

Then if you want to see what is happening type this in the termional

tmux a -t fanshim
