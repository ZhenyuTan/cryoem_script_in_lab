#!/usr/bin/env python

instar='Extract/job053/particles.star'
xdim=3838 
ydim=3710
boxsize=350#unbinned boxsize
exclude_edge=5 #exclude particles that fall within this gap
newfile=open('%s_outliers_removed.star' %(instar[:-5]),'w')

ylim1=exclude_edge
ylim2=ydim-exclude_edge
xlim1=exclude_edge
xlim2=xdim-exclude_edge

for line in open(instar,'r'):
	if len(line.split())<12:
		newfile.write(line)
		continue
	xcoord=float(line.split()[0])	
	ycoord=float(line.split()[1])
	
	x1=xcoord-(boxsize/2)
	x2=xcoord+(boxsize/2)
	y1=ycoord-(boxsize/2)
	y2=ycoord+(boxsize/2)

	badflag=0
	if x1>xlim2 or x1<xlim1: 
		#print 'bad1'
		badflag=1
	if x2>xlim2 or x2<xlim1:
                #print 'bad2'
		badflag=1
	if y1>ylim2 or y1<ylim1:
                #print 'bad3'
		badflag=1
	if y2>ylim2 or y2<ylim1:
                #print 'bad4'
		badflag=1

	if badflag == 0: 
		newfile.write(line)
