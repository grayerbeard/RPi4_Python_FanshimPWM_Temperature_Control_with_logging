# RPi4_Python_FanshimPWM_Temperature_Control_with_logging
R Pi 4 with Fanshim Cooling controlled with PWM, temperature control suitable for smartplugs or SCR with PWM and with temperature logging and remote monitoring.  All separate funtions split among classes.

following items in this repository are working OK

+Common Use classes
- utility.py
* buffer_log.py
* text_buffer.py
* tmux_start.sh
* tmux_stop.sh

Test the text buffer
* test_text_buffer.cfg
* test_text_buffer.py

Fanshim PWM Speed Control
* cpu_monitor.py
* cpu_monitor_config.py
* cpu_monitor_config.cfg
* cpu.py

following items are not yet developed to working versions
* config.py old version for reference
* config.cfg old version for reference
* cpu_temp_log.py old version for reference



* my_sensors.py
* schedule.py
* sensor_data.csv
* smartplug.py
* temp_control.py
* temp_control_config.py
* temp_control_config.cfg
* watch_dog.py

following are provided as a template needing edit to work on a system
* ftp_cred.csv
* mount_drives.py
* mount_drives.sh
