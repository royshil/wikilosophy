import multiprocessing
import pickle
import glob,pprint,sys,re

def combine_recurse(hist1,hist2):
	hist1_k = list(set(hist1.keys()) - set(['w']))

	if 'w' in hist1.keys(): hist1['w'] += hist2['w'] 

	for v2 in list(set(hist2.keys()) - set(['w'])):
		if v2 in hist1.keys():
			#print "combine ",v2
			# already exists - combine recurse
			#hist1[v2]['w'] = hist1[v2]['w'] + hist2[v2]['w']
			combine_recurse(hist1[v2],hist2[v2])
		else:
			hist1[v2] = hist2[v2]	# just add		


def reduce(hist_q):
#	if hist_q.empty(): return

	# get two histograms
	(hist1,hist2) = hist_q.get(True)
	
	return combine(hist1,hist2)

def combine(hist1,hist2):
	print "combining: {0} and {1}".format(hist1,hist2)

	# combine them
	hist1_o = pickle.Unpickler(open(hist1,'r')).load()
	hist2_o = pickle.Unpickler(open(hist2,'r')).load()
	combine_recurse(hist1_o,hist2_o)	

	# pickle the result
	filename = '_'+hist1
	pickle.Pickler(open(filename,'w')).dump(hist1_o)

	return filename

def flatten(hist):
	flat = {}
	if hist is None or hist.keys() is None: return {}
	for i in hist.keys():
		if not isinstance(hist[i],{}.__class__) or hist[i] is None: continue
		flat[i] = hist[i]
		subflat = flatten(hist[i])
		if subflat is not None and len(subflat)>0: flat.update(subflat)

def newcombine(hist1,hist2):
	for v in hist2.keys():
		if v == '_w': continue

		if v in hist1:
			hist1[v]['_w'] = hist1[v]['_w'] + hist2[v]['_w']
#			hist1[v].update(hist2[v])
			for k in hist2[v]:
				if k in hist1[v]: hist1[v][k] = hist1[v][k] + hist2[v][k]
				else: hist1[v][k] = hist2[v][k]
			if len(hist1[v]) > 80:
				#pprint.PrettyPrinter(2).pprint(hist[v])
				histogram_temp = sorted(hist1[v].items(),key=lambda x: x[1])
				#pprint.PrettyPrinter(2).pprint(histogram_temp[-25:])
				hist1[v] = dict(histogram_temp[-25:])	
				#print "cull internal ",v, ", biggest:",histogram_temp[-25],"now:",len(hist[v])
		else:
			hist1[v] = hist2[v]

def textify_title(title):
	title = re.sub("\_"," ",title) #underscores
	title = re.sub("\s+"," ",title) #extra spaces
	return " ".join([w.capitalize() for w in title.split()]) #capitalize

if __name__=="__main__":
#	q = multiprocessing.Queue()
#	q.put(('histogram_1979_ml1.pickle','histogram_1990_great_american_bank_classic.pickle'))
#	reduce(q)
	files = glob.glob("histogram_*")
#	newh = combine(files.pop(),files.pop())
#	for filen in glob.glob("histogram_*"):
#		newh = combine(newh,filen)	

	print >>sys.stderr, "load ",files[-1]
	hist = pickle.Unpickler(open(files.pop(),'r')).load()
	for f in files:
		print >>sys.stderr, "combine with ",f
		newcombine(hist,pickle.Unpickler(open(f,'r')).load())
	#pprint.PrettyPrinter(2).pprint(hist)

	print "digraph {"
	for k in hist:
		print "{0} [weight={1},label=\"{2}\"];".format(k,hist[k]['_w'],textify_title(k))
		for v in hist[k]:
			if v == '_w': continue
			print "{1} -> {0} [weight={2}];".format(k,v,hist[k][v])	
	print "}"
