#!/bin/bash

cmd_coolq="sudo docker run \
 -p 9000:9000 -p 5700:5700 \
 -e COOLQ_ACCOUNT=3309196071 -e COOLQ_URL='http://dlsec.cqp.me/cqp-xiaoi' \
 -v /home/islab/coolq:/home/user/coolq -v /home/islab/src/FFXIVBOT/card:/home/user/coolq/data/image/card\
 coolq/wine-coolq"

tmux new-session -d -s ffxivbot
tmux new-window -t ffxivbot:1 "$cmd_coolq"
tmux split-window -t ffxivbot:1 -h /bin/bash
tmux select-window -t ffxivbot:1
tmux -2 attach-session -t ffxivbot

