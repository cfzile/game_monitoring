#!/bin/bash
count=$(ls logs | wc -l)
name=$(date --iso-8601=d)_$count
#touch logs/$name
pkill update_info.py -f
echo 'run_1'
python3 update_info.py 1 > logs/$name:1
echo 'run_2'
python3 update_info.py 2 > logs/$name:2
echo 'run_3'
python3 update_info.py 3 > logs/$name:3
#echo 'run_4'
#python3 update_info.py 4 > logs/$name:4
#echo 'run_5'
#python3 update_info.py 5 > logs/$name:5
#echo 'run_6'
#python3 update_info.py 6 > logs/$name:6
