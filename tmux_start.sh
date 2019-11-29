#!/bin/bash
cd /home/pi/fanshim
echo looking to kill any old tmux fanshim session
tmux kill-session -t fanshim
echo now new tmux fanshim session 
tmux new-session -d -s fanshim 'python3 fanshim.py'

