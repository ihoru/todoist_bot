#!/bin/bash

# Calling this script:
# ./scripts/notebook.sh

DIR=`dirname $0`;
cd ${DIR}/..;
source $PWD/ENV/bin/activate;
jupyter notebook $@;
