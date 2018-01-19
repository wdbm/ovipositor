#!/bin/bash

while true; do
    sudo python3 ovipositor.py                               \
        --socket=80                                          \
        --restart_regularly                                  \
        --restart_interval=300                               \
        --home="index.html"
done
