from kyotocabinet import *
import sys

# create the database object
db = DB()

# open the database
if not db.open("tempcabinet.kch", DB.OWRITER | DB.OCREATE):
	print >>sys.stderr, "open error: " + str(db.error())
	sys.exit(0)

if not db.clear():
	print >>sys.stderr, "cant clear "+str(db.error())
	sys.exit(0)

inc = 0

fh = open(sys.argv[1],'r')
for line in fh.xreadlines():
#	if line == None:
#		break
	if line.find(" -> ") == -1: continue
	line = line.strip()

	try:
		(k,v) = line.split(" -> ")
	except(ValueError):
		continue
	v = v.strip()
	k = k.strip()
	db[k] = v
#	if not db.get(v):
#		db[v] = 0	

#	def incproc(key,value):
#		return value + 1
#	db.accpet(v,incproc)	# attempt using procedure
#	db[v] = int(db[v]) + 1

print >>sys.stderr, "done reading file"

db.copy("backup.kch") # make a backup

# close the database
if not db.close():
    print >>sys.stderr, "close error: " + str(db.error())

