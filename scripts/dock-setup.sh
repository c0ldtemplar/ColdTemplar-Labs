#!/bin/bash
xrandr --output eDP-1-0 --off \
       --output DP-0.1 --primary --mode 1920x1080 --rate 60 --pos 0x0 \
       --output DP-0.3 --mode 1920x1080 --rate 60 --pos 1920x0 --right-of DP-0.1
