import zmq
import time
import sys,re,os
from cStringIO import StringIO

def roll_to_start(fh):
	last_pos = fh.tell()
	line = fh.readline()
	while line.find('<page>') == -1:
		last_pos = fh.tell()
		line = fh.readline()
	fh.seek(last_pos)
	

print "opening zmq server"

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

noncharre = re.compile('\W')

fh = open('enwiki-latest-pages-articles.xml','r')
roll_to_start(fh)
print "starting pages at ",fh.tell()

print "serving clients"
serving = True
while serving:
	#  Wait for next request from client
	message = socket.recv()
	#print "Received request: ", message

	if message.find("START_OVER") > -1:
		print "starting over..."
		roll_to_start(fh)
		continue

	page = StringIO()
	gotid = False
	filerunning = True
	response = ''
	while filerunning:
		#next = sys.stdin.readline()         # read a one-line string
		next = fh.readline()
		if not next:                        # or an empty string at EOF
			filerunning = False	
			serving = False
			response = "ALL_DONE"	
		else:	
	#		if not next.find('<page') > -1:
	#			continue			#roll forward untill beginning of page

			page.write(next)

			if next.strip().find('<title>') > -1:
				title = next[next.find('title>')+6:next.find('</title')]
#				title = noncharre.sub('-',title)
#				title = title[:200]
	#
	#		if not gotid and next.strip().find('<id>') > -1:
	#			title = next[next.find('<id>')+4:next.find('</id')] + '_' + title
	#			gotid = True

			#done readine one page
			if next.strip().find('</page') > -1:
				response = page.getvalue()
				page.close()
				page = StringIO()
				gotid = False
				filerunning = False

	#print "serving: ",title
	#  Send reply back to client
	socket.send(response)

