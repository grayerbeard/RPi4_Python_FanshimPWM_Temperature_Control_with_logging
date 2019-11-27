# RPi4_Python_FanshimPWM_Temperature_Control_with_logging
R Pi 4 with Fanshim Cooling controlled with PWM, temperature control suitable for smartplugs or SCR with PWM and with temperature logging and remote monitoring.  All separate functions split among classes.

This repository MASTER is my central place for my projects on temperature heating and cooling control  with  looging and remote control.

I intend putting fully functiining applications in branchez abd the furst is for thepimorini fanshim pwm control.

To clone just the pwm_fanshim branch use this command

 git clone https://github.com/grayerbeard/RPi4_Python_FanshimPWM_Temperature_Control_with_logging.git -b pwm_fanshim --single-branch /home/pi/fanshim/

For further details switch to that branch or look on my web site at https://www.smalle.uk/r-pi-4-blog


following items in this repository are working OK
<ul>
<li>Common Use classes</li>
  <ul>
    <li>config.cfg</li>
    <li>config.py</li>
    <li>utility.py</li>
    <li>buffer_log.py</li>
    <li>text_buffer.py</li>
    <li>tmux_start.sh</li>
    <li>tmux_stop.sh</li>
  </ul>
<li>Test the text buffer</li>
  <ul>
<li>test_text_buffer.py</li>
  </ul>
<li>Fanshim PWM Speed Control</li>
  <ul>
    <li>cpu_monitor.py</li>
    <li>cpu.py</li>
    <li>tmux_stress.sh</li>
  </ul>
</ul>
following items are not yet developed to working versions
<ul>
  <li>Temperature Control using Smartplug or SCR with PWM</li>
<ul>
  <li>my_sensors.py</li>
  <li>schedule.py</li>
  <li>sensor_data.csv</li>
  <li>smartplug.py</li>
  <li>temp_control.py</li>
  <li>temp_control_config.py</li>
  <li>temp_control_config.cfg</li>
  <li>watch_dog.py</li>
 </ul>
</ul>
following are provided as a template needing editing to work on a particular system
<ul>
 <ul> 
  <li>ftp_cred.csv</li>
  <li>mount_drives.py</li>
  <li>mount_drives.sh</li>
</ul>
  </ul>

