#!/bin/bash
cd /home/pi/fanshim
echo looking to kill any old tmux stress session
tmux kill-session -t stress
echo now new tmux stress session 100% load 15 minutes
tmux new-session -d -s stress 'while true; do vcgencmd measure_clock arm; vcgencmd measure_temp; sleep 10; done& stress -c 4 -t 900s'
