#!/bin/bash

declare -px > /tmp/.env
chmod 0644 /tmp/.env
uvicorn basestation_server:app1 --reload --port 8000
