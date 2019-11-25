#!/bin/bash
cd /home/pi/fanshim
tmux kill-session -t stress
tmux new-session -d -s stress 'while true; do vcgencmd measure_clock arm; vcgencmd measure_temp; sleep 10; done& stress -c 4 -t 900s'
