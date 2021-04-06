#!/bin/bash
pkill masterserver.py -f
count=$(ls logs | wc -l)
name=$(date --iso-8601=d)_$count.txt
touch logs/$name
rm pidfile
python3 masterserver.py ./logs/$name > ./logs/$name:run