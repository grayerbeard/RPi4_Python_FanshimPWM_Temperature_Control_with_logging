# RPi4_Python_FanshimPWM_Temperature_Control_with_logging
R Pi 4 with Fanshim Cooling controlled with PWM, temperature control suitable for smartplugs or SCR with PWM and with temperature logging and remote monitoring.  All separate funtions split among classes.

following items in this repository are working OK
<ul>
<li>Common Use classes</li>
  <ul>
    <li>utility.py</li>
    <li>buffer_log.py</li>
    <li>text_buffer.py</li>
    <li>tmux_start.sh</li>
    <li>tmux_stop.sh</li>
  </ul>
<li>Test the text buffer</li>
  <ul>
<li>test_text_buffer.cfg</li>
<li>test_text_buffer.py</li>
  </ul>
<li>Fanshim PWM Speed Control/li>
  <ul>
    <li>cpu_monitor.py</li>
    <li>cpu_monitor_config.py</li>
    <li>cpu_monitor_config.cfg</li>
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
 
following are just back ups of old versions for reference
<ul>
  <ul>
    <li>config.py old version for reference</li>
    <li>config.cfg old version for reference</li>
    <li>cpu_temp_log.py old version for reference</li>
  </ul>
</ul>
