#!/bin/bash

DIR=`dirname $0`;
cd ${DIR}/..;
source $PWD/ENV/bin/activate;
python run.py runserver --host todoist-l.iho.su --port 8100;
