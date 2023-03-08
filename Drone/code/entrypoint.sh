#!/bin/bash

declare -px > /tmp/.env
chmod 0644 /tmp/.env
python drone_main.py