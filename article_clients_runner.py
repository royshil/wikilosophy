from multiprocessing import Pool
from zmq_wikiarticle_client import *

def f(num):
	filenm = 'links_{0}.DOT'.format(num)
	print "start links file ",filenm
	client = article_client(open(filenm,'w'),number=num)
	client.start_client()
	return True

NPROCESSES = 6

if __name__ == '__main__':
    #zmq_wikiarticle_client.verbose = True
	context = zmq.Context()

	#  Socket to talk to server
#	print "Connecting to article server..."
#	socket = context.socket(zmq.REQ)
#	socket.connect ("tcp://localhost:5555")

#	print "ordering server to restart"
#	socket.send("START_OVER")

	pool = Pool(processes=NPROCESSES)              # start worker processes

	pool.map(f, range(NPROCESSES))          
