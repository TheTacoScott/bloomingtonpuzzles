#!/bin/bash
if [ -f "$1" ]
then
  for min in `seq 100000 100000 1000000`
  do 
    for max in `seq $min 100000 1000000`
    do 
      echo "$min $max"
      python wine.py --input "$1" --min-buffer=$min --max-buffer=$max 
      sleep 0.01
    done 
  done
else
  echo "Must pass a filename as first arg"
fi
