import zmq,re,sys,traceback
from lxml import etree
import simpleWiki

verbose = False 

def removeBalanced(article_text,delim_open,delim_close):
	stack = []
	ptr = 0
	nothingDone = False
	while not nothingDone: #article_text.find(delim_open) > -1 or article_text.find(delim_close) > -1 or  # not efficient...
		nothingDone = True
		open_pos = article_text.find(delim_open,ptr)
		close_pos = article_text.find(delim_close,ptr)
		if open_pos > -1 and open_pos < close_pos:
			ptr = open_pos + len(delim_open) 
			if verbose: 
				print "found ",delim_open," at ",open_pos
			if len(stack)>0 and open_pos == stack[-1]:  # in case we already found this..
				if verbose:
					print 'skipping...'
				continue
			stack.append(open_pos)
			nothingDone = False
		elif close_pos > -1:
			if verbose:
				print "found ",delim_close," at ",close_pos
			#ptr = close_pos
			try:
				from_pos = stack.pop()
				to_pos = close_pos+len(delim_close)
				article_text = article_text[:from_pos] + article_text[to_pos:]
				if len(stack) > 0:
					ptr = stack[-1] + len(delim_open)
				else:
					ptr = 0
				if verbose:
					print "delete {0} to {1}, ptr = {2}".format(from_pos,to_pos,ptr)
				nothingDone = False
			except(IndexError):
				break	#some error i probably don't want to deal with...
	return article_text

def getFirstLink(article_text):
	firstlink = article_text[article_text.find('[[')+2:article_text.find(']]')]
	if firstlink.find('|') > -1:
		firstlink = firstlink[:firstlink.find('|')]
	return firstlink.strip().lower()

def normalizeLink(link):
	link = re.sub('\#.*$','',link)
	link = re.sub('\W','_',link.strip().lower())
	return link

def writeLink(title,link,fh):
	link = normalizeLink(link)
	title = normalizeLink(title)
	if not link == title and len(link) != 0 and len(title) != 0:
		linkstr = "{0} -> {1}".format(title,link)
		if verbose: print "link: ", linkstr 
		fh.write(linkstr+'\n')
		fh.flush()


class article_client:
	def __init__(self,outputfile,number=-1):
		self.linksFiles = [idx+"_"+outputfile for idx in ["third","forth","fifth"]] #outputfile
		self.linksFilesHandles = [open(filename,'w') for filename in self.linksFiles]
		self.title = 'temp'
		self.number = number

	def start_client(self):
		context = zmq.Context()

		#  Socket to talk to server
		print "Connecting to article server..."
		socket = context.socket(zmq.REQ)
		socket.connect ("tcp://localhost:5555")

#		self.linksFile = output_file #'links_'+sys.argv[1]+'.DOT','w')

		while True:
			try:
				if verbose:
					print "Sending request "
				socket.send ("GIVE_ARTICLE")

				#  Get the reply.
				message = socket.recv()
				#print "Received reply [", message, "]"
				if message.find('ALL_DONE') == 0:
					break

				self.parseResponse(message)
				 
					
				#break
				#continue
			except(KeyboardInterrupt):
				print "exiting..."
				break

	def parseResponse(self,message):
		root = etree.fromstring(message)
		
		self.title = root.find("title").text.encode('ascii','replace').strip().lower()
		#print >> sys.stderr, self.title, "[",self.number,"]"

		if verbose:
			print "parsing article ",self.title

		try:
			article_text = root.xpath("/page/revision/text")[0].text.encode('ascii','replace')
		except(AttributeError):
			if verbose:
				print "can't read text!"
			return False

		if re.search('\{\{(disambig.*?|geodis)\}\}',article_text) is not None or self.title.find('(disambiguation)') > -1:
			if verbose:
				print "This is a disambig..."
			#break	
			return False


		if verbose:
			print "is this a redirect? ", root.find("redirect") != None

		#if root.find("redirect") != None:
		#link = getFirstLink(article_text)
		try:
			#link = simpleWiki.getMediaWikiFirstLink(article_text)
			links = simpleWiki.getNFirstLinks(article_text,5) # get first 5 links
			#link = simpleWiki.getNthLink(article_text,2)
			for i in range(0,2):				# scan the last 3 (link # 3,4,5)
				link = links[2+i]
				writeLink(self.title,link,self.linksFilesHandles[i]) # write each link to a diff file
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback, limit=1, file=sys.stderr)
		 	

		return True


		
#		return self.parseText(article_text)	

	def parseText(self,article_text):
		try:
			#link = simpleWiki.getMediaWikiFirstLink(article_text)
			link = simpleWiki.getNthLink(article_text,2)
			writeLink(self.title,link,self.linksFile)
		except:
			exc_type, exc_value, exc_traceback = sys.exc_info()
			traceback.print_tb(exc_traceback, limit=1, file=sys.stderr)
		'''
		article_text = removeBalanced(article_text,'{{','}}')
		#article_text = removeBalanced(article_text,'(',')')

	#		article_text = re.sub(r'\{\{[\s\S]*?\}\}','',article_text)
		article_text = re.sub(r'\[\[([Ii]mage|[Ff]ile)[\s\S]*?\]\]\n','',article_text)  # remove image links
	#		article_text = re.sub(r'\([\s\S]*?\)','',article_text) 			 # remove paretheses
		article_text = re.sub(r'&lt;\!--[\s\S]*?--&gt;','',article_text)	# remove html remarks
		article_text = re.sub(r'<!--[\s\S]*?-->','',article_text)	# remove html remarks
		article_text = re.sub(r'\:\'\'.*?\'\'','',article_text)			# remove wiki italics
		article_text = re.sub(r'<ref[\s\S]*?</ref>','',article_text)		# revmoe refs
		article_text = re.sub(r'\(from \[\[[\s\S]*?\)','',article_text)
		article_text = re.sub(r'\[\[wikt\:[\s\S]*?\]\]','',article_text) 	# wikitionary links

		if verbose:
			print article_text	

		firstlink = getFirstLink(article_text)
		writeLink(self.title,firstlink,self.linksFile)
		'''

		return True

if __name__ == "__main__":
	client = article_client(sys.stdout)
#	client.start_client('output'+sys.argv[1]+'.DOT')
	if len(sys.argv) > 2 and sys.argv[2] == 'verbose': verbose = True
	client.parseText(open(sys.argv[1],'r').read())
