#!/bin/bash
gunicorn --bind 0.0.0.0:4000 --reuse-port --reload main:app
