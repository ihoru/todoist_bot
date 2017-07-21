#!/usr/bin/env bash

# Calling this script:
# ./scripts/install_requirements.sh # good for production
# or
# ./scripts/install_requirements.sh 1 # to install from freeze-file (the top-level requirements, that app use). Good for development
# ! it will automatically create ENV directory for installing dependencies there !

DIR=`dirname $0`;
cd ${DIR}/..;
if [[ ! -d $PWD/ENV ]];
then
	$PWD/scripts/virtualenv.sh;
fi;
F='';
if [[ -n $1 ]];
then
	F='-to-freeze';
fi;
source $PWD/ENV/bin/activate;
pip install --compile -r $PWD/requirements$F.txt;
