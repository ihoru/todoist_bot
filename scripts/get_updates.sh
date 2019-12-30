#!/bin/bash

DIR=`dirname $0`;
cd ${DIR}/..;
source $PWD/ENV/bin/activate;
pkill -f "tail \-n0 \-f $PWD/logs/"
tail -n0 -f $PWD/logs/*/debug.log &
python run.py bot get_updates;
