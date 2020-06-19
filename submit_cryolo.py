#!/usr/bin/env python

import shutil
import optparse
from sys import *
import os,sys,re
from optparse import OptionParser
import glob
import subprocess
from os import system
import linecache
import time

#=========================
def setupParserOptions():
        parser = optparse.OptionParser()
        parser.set_usage("%prog --dir=<folder with mrc frames> --diam=<diameter in pixels>\n")
        parser.add_option("--dir",dest="dir",type="string",metavar="DIRECTORY",
                    help="Specify directory with .mrc micrographs for picking with cryolo")
	parser.add_option("--diam",dest="diam",type="int",metavar="DIAMETER",
                    help="Specify diameter of particle (in pixels)")        
	parser.add_option("--thresh",dest="thresh",type="float",metavar="THRESHOLD",default=0.2,
                    help="Specify threshold for picking (Default=0.2, usually works!)")
	parser.add_option("--negstain",action="store_true",dest="stain",default=False,
		    help="Specify this flag for negative stain micrographs")
	parser.add_option("-d", action="store_true",dest="debug",default=False,
                    help="debug")

        options,args = parser.parse_args()

        if len(args) > 0:
                parser.error("Unknown commandline options: " +str(args))
        if len(sys.argv) <= 1:
                parser.print_help()
                sys.exit()
        params={}
        for i in parser.option_list:
                if isinstance(i.dest,str):
                        params[i.dest] = getattr(options,i.dest)
        return params

#==============================
if __name__ == "__main__":

        params=setupParserOptions()

	if not os.path.exists(params['dir']):
		print 'Error: Input directory does not exist %s' %(params['dir'])
		sys.exit()

	#Write config script
	if params['stain'] is False:
		o1=open('%s/config.json' %(params['dir']),'w')
		o1.write("""    {
    "model" : {
       	"architecture":         "PhosaurusNet",
        "input_size":           1024,
       	"anchors":              [%i,%i],
        "max_box_per_image":    1000,
       	"num_patches":          1,
        "filter":               [0.1,"%s/tmp_filtered"]
      }
    }""" %(params['diam'],params['diam'],params['dir']))
		o1.close()

		o1=open('%s/submit_cryolo.sh' %(params['dir']),'w')
		o1.write("""#!/bin/bash
###Inherit all current environment variables
#PBS -V
### Job name
#PBS -N crYOLO
### Keep Output and Error
#PBS -k eo
### Queue name
#PBS -q batch
### Specify the number of nodes and thread (ppn) for your job.
#PBS -l nodes=1:ppn=20
### Tell PBS the anticipated run-time for your job, where walltime=HH:MM:SS
#PBS -l walltime=12:00:00
#################################
NSLOTS=$(wc -l $PBS_NODEFILE|awk {'print $1'})

### Switch to the working directory;
cd $PBS_O_WORKDIR
### Run:
singularity exec /lsi/groups/cryoem-workshop/shared_software/cryolo/ubuntu_cryolo_cudnn.simg cryolo_predict.py -c %s/config.json -w /lsi/groups/cryoem-workshop/shared_software/cryolo/gmodel_phosnet_20190516.h5 -i %s/ -o %s/cryolo -t %f > %s/run.out 2> %s/run.err < /dev/null
#Cleanup
rm -rf %s/tmp_filtered""" %(params['dir'],params['dir'],params['dir'],params['thresh'],params['dir'],params['dir'],params['dir']))
		o1.close()

		cmd='qsub %s/submit_cryolo.sh' %(params['dir'])
		subprocess.Popen(cmd,shell=True).wait()


	if params['stain'] is True:
		o1=open('%s/config.json' %(params['dir']),'w')
		o1.write("""    {
    "model" : {
       	"architecture":         "PhosaurusNet",
        "input_size":           1024,
       	"anchors":              [%i,%i],
        "max_box_per_image":    1000,
       	"num_patches":          1
      }
    }""" %(params['diam'],params['diam']))
		o1.close()

		o1=open('%s/submit_cryolo.sh' %(params['dir']),'w')
		o1.write("""#!/bin/bash
###Inherit all current environment variables
#PBS -V
### Job name
#PBS -N crYOLO
### Keep Output and Error
#PBS -k eo
### Queue name
#PBS -q batch
### Specify the number of nodes and thread (ppn) for your job.
#PBS -l nodes=1:ppn=20
### Tell PBS the anticipated run-time for your job, where walltime=HH:MM:SS
#PBS -l walltime=12:00:00
#################################
NSLOTS=$(wc -l $PBS_NODEFILE|awk {'print $1'})

### Switch to the working directory;
cd $PBS_O_WORKDIR
### Run:
singularity exec /lsi/groups/cryoem-workshop/shared_software/cryolo/ubuntu_cryolo_cudnn.simg cryolo_predict.py -c %s/config.json -w /lsi/groups/cryoem-workshop/shared_software/cryolo/gmodel_phosnet_negstain_20190226.h5 -i %s/ -o %s/cryolo -t %f > %s/run.out 2> %s/run.err < /dev/null

""" %(params['dir'],params['dir'],params['dir'],params['thresh'],params['dir'],params['dir']))
		o1.close()

		cmd='qsub %s/submit_cryolo.sh' %(params['dir'])
		subprocess.Popen(cmd,shell=True).wait()

	print '\ncrYOLO job submitted to the cluster. \n\nOutput particle picks can be found in:\n%s/cryolo/\n\nOutput log files are:\n%s/run.out\n%s/run.err\n' %(params['dir'],params['dir'],params['dir'])
