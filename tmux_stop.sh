#!/bin/bash
cd /home/pi/fanshim
echo looking to kill any old fanshim stress session
tmux kill-session -t fanshim
echo looking to kill any old tmux stress session
tmux kill-session -t stress
