#!/bin/bash
cd /home/pi/fanshim
echo looking to kill any tmux stress session
tmux kill-session -t stress
