#!/bin/bash
cd /home/pi/code
tmux kill-session -t ctrl
tmux kill-session -t cpu
tmux kill-session -t fan
