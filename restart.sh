#!/bin/bash
pkill --signal  SIGINT  uwsgi
git pull
count=$(ls logs | wc -l)
name=$(date --iso-8601=d)_$count.txt
touch logs/$name
uwsgi --logto ./logs/$name --socket localhost:9000 --module siteroot.wsgi --master --workers 4 &