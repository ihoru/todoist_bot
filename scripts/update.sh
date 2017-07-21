#!/usr/bin/env bash

DIR=`dirname $0`;
cd ${DIR};
if [[ ! -d ENV ]];
then
	# you can make this link in the root dir:
	# ln -s scripts/update.sh
	# just because it is faster to call it
	cd ..;
fi;
source $PWD/ENV/bin/activate;

git fetch;
STASH=$([[ `git stash` = 'No local changes to save' ]]);
git pull;
if [[ $STASH -eq 0 ]];
then
	git stash pop >/dev/null;
fi;

supervisorctl restart todoist_web