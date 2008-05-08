#!/bin/bash

DBFILE=/var/tmp/`whoami`/aquilondb/aquilon.db
if [ -r "$DBFILE" ] ; then
	mv "$DBFILE" "$DBFILE.saved"
	echo "moved existing db to '$DBFILE.saved'"
fi

IPY='/ms/dist/python/PROJ/ipython/0.7.2/bin/ipython '

echo starting at
/bin/date

time ./subtypes.py
echo
time ./location.py
echo
time ./network.py
echo
time ./roles.py
echo
time ./auth.py
echo
time ./configuration.py
echo
time ./hardware.py
echo
time ./interface.py
echo
time ./systems.py
echo
time ./service.py
echo Run population_scripts if you need to
#time ./population_scripts.py
echo completed at
/bin/date
