#!/bin/bash

while true; do
    ovipositor                 \
        --socket=80            \
        --restart_regularly    \
        --restart_interval=300 \
        --home="index.html"
done
