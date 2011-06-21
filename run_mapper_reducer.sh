#!/bin/sh

python -c "from kyotocabinet import *; db=DB(); db.open('tempcabinet.kch',DB.OREADER); db.dump_snapshot('tempcabinet.snapshot'); db.close()" 
rm histogram_* 
nice python ../mapper.py > /dev/null 
nice python ../reducer.py > output5.dot
