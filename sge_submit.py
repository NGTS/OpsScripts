#!/usr/local/python/bin/python
# python script to submit SGE jobs to queue

import os
import argparse as ap

# function to parse the command line
def argParse():
	parser=ap.ArgumentParser(description="Script to submit SGE jobs to queue")
	parser.add_argument('jobfile',help='file with job parameters')
	return parser.parse_args()

args=argParse()
os.system('/usr/local/sge/bin/lx-amd64/qsub %s' % (args.jobfile))
