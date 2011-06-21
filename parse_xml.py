#!/usr/bin/python

import sys,re,os
from cStringIO import StringIO

noncharre = re.compile('\W')

if __name__ == "__main__":
	page = StringIO()
	gotid = False
	while 1:
		next = sys.stdin.readline()         # read a one-line string
		if not next:                        # or an empty string at EOF
			break
		
		page.write(next)

		if next.strip().find('<title>') > -1:
			title = next[next.find('title>')+6:next.find('</title')]
			title = noncharre.sub('-',title)
			title = title[:200]

		if not gotid and next.strip().find('<id>') > -1:
			title = next[next.find('<id>')+4:next.find('</id')] + '_' + title
			gotid = True
		
		if next.strip().find('</page') > -1:
			filename = title+'.xml'
			if not os.path.exists(filename): 
				open(filename,'w').write(page.getvalue())
			page.close()
			page = StringIO()
			gotid = False

