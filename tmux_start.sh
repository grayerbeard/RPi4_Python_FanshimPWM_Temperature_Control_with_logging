#!/bin/bash
cd /home/pi/code
#tmux kill-session -t wd
#tmux kill-session -t ctrl
#tmux kill-session -t test
#tmux kill-session -t mnt
tmux kill-session -t cpu
#tmux new-session -d -s wd 'python3 watch_dog.py'
#tmux new-session -d -s ctrl 'python3 temp_control.py'
tmux new-session -d -s cpu 'python3 cpu_monitor.py'
#tmux new-session -d -s mnt 'python3 mount_drives.py'
#tmux new-session -d -s test 'python3 test_text_buffer.py'

