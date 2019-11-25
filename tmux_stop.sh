#!/bin/bash
cd /home/pi/fanshim
tmux kill-session -t fanshim
tmux kill-session -t stress
