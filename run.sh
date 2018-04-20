#!/usr/bin/env sh
exec su -s /bin/sh dcu -c "/usr/local/bin/celery -A run worker -l INFO --without-gossip --without-heartbeat --without-mingle"
