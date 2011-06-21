from kyotocabinet import *
import sys
from operator import itemgetter
from pprint import PrettyPrinter
import pickle
from multiprocessing import Pool
import time

pp = PrettyPrinter(indent = 4)

def followOne(k,v,db,histogram,update_hist):
	# find the "terminal" node for this source 
	# (not efficient, can utilize the path for other sources)
	visited = [v]
	while db[v] and db[v] not in visited:
		#print "\t ->", db[v]
		visited.append(db[v])	# break the cycle 
		v = db[v]
		if v == 'philosophy': break
	#if v not in ['philosophy','data_storage_device','association_football','transmission__telecommunications_','comparison','accounting_software','advocacy_group','recording','bloom','isotorpy']:
		#print k,'\n\t->',
		#print "\n\t->".join(visited)

	if histogram is None:
		print "\n\t->".join(visited)
		return

	for i in range(len(visited)-1):
		v = visited[i]
		v1 = visited[i+1]
		if not v1 in histogram: 
			histogram[v1] = {'_w':1,v:1}
		else:
			histogram[v1]['_w'] = histogram[v1]['_w'] + 1
			if not v in histogram[v1]: histogram[v1][v] = 0
			histogram[v1][v] = histogram[v1][v] + 1
'''
	if v not in histogram:
		if update_hist: 
			histogram[v] = {'w':1}
			if len(visited)>1: histogram[v][visited[-2]] = {'w':1}	# keep populating histogram
			if len(visited)>2: histogram[v][visited[-2]][visited[-3]] = {'w':1}
			if len(visited)>3: histogram[v][visited[-2]][visited[-3]][visited[-4]] = {'w':1}
			if len(visited)>4: histogram[v][visited[-2]][visited[-3]][visited[-4]][visited[-5]] = {'w':1}


	else:
		histogram[v]['w'] = histogram[v]['w'] + 1
		if len(visited)>1: 
			if visited[-2] not in histogram[v]: histogram[v][visited[-2]] = {'w':1}
			else: histogram[v][visited[-2]]['w'] = histogram[v][visited[-2]]['w'] + 1
		if len(visited)>2: 
			if visited[-3] not in histogram[v][visited[-2]]: histogram[v][visited[-2]][visited[-3]] = {'w':1}
			else: histogram[v][visited[-2]][visited[-3]]['w'] = histogram[v][visited[-2]][visited[-3]]['w'] + 1
 		if len(visited)>3: 
			if visited[-4] not in histogram[v][visited[-2]][visited[-3]]: histogram[v][visited[-2]][visited[-3]][visited[-4]]= {'w':1}
			else: histogram[v][visited[-2]][visited[-3]][visited[-4]]['w'] = histogram[v][visited[-2]][visited[-3]][visited[-4]]['w'] + 1
 		if len(visited)>4: 
			if visited[-5] not in histogram[v][visited[-2]][visited[-3]][visited[-4]]: histogram[v][visited[-2]][visited[-3]][visited[-4]][visited[-5]] = {'w':1}
			else: histogram[v][visited[-2]][visited[-3]][visited[-4]][visited[-5]]['w'] = histogram[v][visited[-2]][visited[-3]][visited[-4]][visited[-5]]['w'] + 1
'''

p_db = None

def traverse(start_index):	
	global p_db

	histogram = {}
	update_hist = True

	if p_db is None:
		p_db = DB()
		p_db.open(":") #"tempcabinet.kch",DB.OREADER | DB.ONOLOCK)
		print >>sys.stderr, "load db snapshot"
		p_db.load_snapshot('tempcabinet.snapshot')

	start_time = time.time()

	'''	
	db = DB(opts=[DB.GCONCURRENT])
	# open the database, reader, no lock
	if not db.open("tempcabinet.kch", DB.OREADER | DB.ONOLOCK):
		print >>sys.stderr, "open error: " + str(db.error())
		sys.exit(0)
	'''
	# traverse records
	#for i in range(1,2):
	print "traverse, jump to",start_index

	cur = p_db.cursor()
	cur.jump(start_index)
	count = 0
	#while True:
	for j in range (1,10000):
		rec = cur.get(True)
		if not rec: break
		(k,v) = rec
		followOne(k,v,p_db,histogram,update_hist)
		if j % 1000 == 0: print j,"hist:",len(histogram)

	histogram_temp = sorted(histogram.items(),key=lambda x: x[1]["_w"])
	histogram = dict(histogram_temp[-55:])

	print >>sys.stderr, "done traverse ",start_index

	#cur.jump()
	#while True:
	#	rec = cur.get(True)
	#	if not rec: break
	#	print rec[0],':',rec[1]
#	pp.pprint(sorted(histogram.items(), key=lambda x: x[1]["w"]))

	histogram_name = 'histogram_'+start_index+'.pickle'
	p = pickle.Pickler(open(histogram_name,'w'))
	p.dump(histogram)

	cur.disable()
	#p_db.close()

	print "traverse took {0} seconds".format(time.time()-start_time)

	return histogram_name

if __name__=="__main__":
	
	print >>sys.stderr, "preparing keys jumps for workers"
	db = DB()
	#db.open("tempcabinet.kch",DB.OREADER | DB.ONOLOCK)
	db.open(":")
	print >>sys.stderr, "load db snapshot"
	db.load_snapshot('tempcabinet.snapshot')

	if len(sys.argv) > 1:
		if not db[sys.argv[1]]:
			print "can;t find key ",sys.argv[1]
		else:
			followOne(sys.argv[1],db[sys.argv[1]],db,None,False)
		exit()
#	else:
	cur = db.cursor()
	cur.jump()
	keys = []
	for i in range(0,db.count()):
		rec = cur.get(True)
		if not rec: break
		(k,v) = rec
		if i % 10000 == 0: keys.append(k)

	cur.disable()
	db.close()

	pool = Pool(processes=6)
	try:
		print "histograms created: ",pool.map(traverse,keys)
	except(KeyboardInterrupt):
		print "Killing all processes..."
		pool.terminate()
		pool.join()

#	db.close()
