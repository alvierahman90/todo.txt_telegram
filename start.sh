#!/usr/bin/env bash

source config

# source env if not in docker container
[[ `grep 'docker' /proc/self/cgroup` ]] && source env/bin/activate
python src/bot.py "$TOKEN"
