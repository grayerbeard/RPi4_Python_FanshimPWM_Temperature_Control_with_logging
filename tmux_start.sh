#!/bin/bash
cd /home/pi/fanshim
tmux kill-session -t fanshim
tmux new-session -d -s fanshim 'python3 fanshim.py'

