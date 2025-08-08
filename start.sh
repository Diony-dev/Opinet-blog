#!/usr/bin/env bash

# Inicia la aplicación Gunicorn
gunicorn --workers 4 --bind 0.0.0.0:$PORT wsgi:app