#!/bin/bash

DIR=`dirname $0`;
cd ${DIR}/..;
source $PWD/ENV/bin/activate;
python run.py bot get_updates;
