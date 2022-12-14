#!/bin/bash
docker-compose up --detach &&
tmux new-session -s 'ecs251_demo_spm' \; \
    send-keys  'docker attach bootstrap' C-m \; \
    split-window -h \; \
    send-keys  'docker attach felix' C-m \; \
    split-window -h \; \
    send-keys  'docker attach claudio' C-m \; \
    split-window -h \; \
    send-keys  'docker attach david' C-m \;