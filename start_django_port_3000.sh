#!/bin/bash
gunicorn --bind 0.0.0.0:3000 --reuse-port --reload main:app