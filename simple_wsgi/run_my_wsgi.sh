#!/bin/bash
gunicorn -b 127.0.0.1:8081 my_wsgi
