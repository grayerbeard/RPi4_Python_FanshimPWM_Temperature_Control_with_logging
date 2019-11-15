#!/bin/bash
cd /home/pi/code
tmux new-session -d -s stress 'while trus; do vcgencmd measure_clock arm; vcgencmd measure_temp; sleep 10; done& stress -c 4 -t 900s'

