#!/bin/bash

while true; do
    sudo python3 ovipositor/__init__.py                      \
        --socket=80                                          \
        --restart_regularly                                  \
        --restart_interval=300                               \
        --home="index.html"
done
