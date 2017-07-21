#!/usr/bin/env bash

# Calling this script:
# ./scripts/virtualenv.sh

DIR=`dirname $0`;
cd ${DIR}/..;
virtualenv -p python3.5 --system-site-packages ENV;
# --system-site-packages is needed if you want to be able to use jupyter and ipython if they are installed system-wide