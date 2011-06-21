import subprocess
import sys

def file_len(fname):
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])

flen = file_len(sys.argv[1])
print "size of ",sys.argv[1]," is ",str(flen)


for i in range(2000,flen,2000):
	print "copy {0} to {1}".format(i,i+2000)
	subprocess.call(["/Users/roysh/wikidb/copy_remote.sh",str(i),sys.argv[1]])
