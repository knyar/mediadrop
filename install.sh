#!/bin/sh

set -x -u -e

VENV=$1

if [ -z "$VENV" ]; then
	echo Usage: $0 venv-peth
	exit 3
fi

virtualenv -p python2.7 --no-site-packages "$VENV"
"$VENV/bin/python2.7" setup.py develop

wget https://github.com/sqlalchemy/sqlalchemy/archive/refs/tags/rel_0_7_10.tar.gz &&
	tar xf rel_0_7_10.tar.gz &&
	cd sqlalchemy-rel_0_7_10 &&
	patch -p1 < ../sqlalchemy-rel_0_7_10.patch &&
	"$VENV/bin/python2.7" setup.py install &&
	cd ..

