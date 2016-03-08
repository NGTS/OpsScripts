# work out the LEDs + parked telescope exptimes for
# each telescope

import os, sys
import glob as g
import numpy as np
import argparse as ap
import matplotlib.pyplot as pl

def argParse():
	description="""
		Script to calculate the gain and readnoise automatically
		"""
	parser=ap.ArgumentParser(description=description)
	parser.add_argument("camera_id",type=int,choices=range(801,814,1),help="camera ID")
	parser.add_argument("pag",type=int,choices=[1,2,4],help="pre-amp gain setting")
	return parser.parse_args()

args=argParse()

def calculateGainReadNoise(pag,camera_id):
	biases=g.glob('BIAS-PAG%d*' % (pag))
	flats=g.glob('FLAT-PAG%d*' % (pag)) 
	# load images, exclude 20 pixel boarder around the edge
	f1=np.array(fits.open(flats[0])[0].data[20:2028,40:2048]).astype(np.float)
	f2=np.array(fits.open(flats[1])[0].data[20:2028,40:2048]).astype(np.float)
	b1=np.array(fits.open(biases[0])[0].data[20:2028,40:2048]).astype(np.float)
	b2=np.array(fits.open(biases[1])[0].data[20:2028,40:2048]).astype(np.float)
	df=f1-f2
	db=b1-b2
	g = ( (np.average(f1)+np.average(f2)) - (np.average(b1)+np.average(b2)) ) / (  np.std(df)**2 - np.std(db)**2  )
	rn = ( g * np.std(db) ) / np.sqrt(2.)
	print('[PAG %d] Gain: %.3f' % (g))
	print('[PAG %d] ReadNoise: %.3f' % (rn))
	# plot
	fig = pl.figure(1,figsize=(20,10))
	ax = fig.add_subplot(1, 2, 1, xticks=[], yticks=[])
	ax.imshow(df,cmap=cm.afmhot,vmin=0.8*np.median(df),vmax=1.2*np.median(df),interpolation=None)
	ax.set_title('F1 - F2')
	ax = fig.add_subplot(1, 2, 2, xticks=[], yticks=[])
	ax.set_title('B1 - B2')
	ax.imshow(db,cmap=cm.afmhot,vmin=0.8*np.median(db),vmax=1.2*np.median(db),interpolation=None)
	fig.savefig('autogain-%d-PAG%d.png' % (camera_id,pag),dpi=200)


# exposure times for each pag
pag={1: {811: 6},
	2: {811: 4},
	4: {811: 4}}

try:
	exptime=pag[args.pag][args.camera_id]:
except KeyError:
	print "No stored settings for camera_id: %d with PAG: %d" % (args.camera_id,args.pag)
	print "Exiting"
	sys.exit(1)

home=os.getcwd()
outdir='/local/z_jmcc/autogain/pag%d' % (args.pag)
if os.path.exists(outdir) == False:
	print "Making %s" % (outdir)
	os.mkdir(outdir)
# biases
os.system("/home/ops/ngts/imsequence/imsequence --fastcool --temperature -70 --holdtemp --outdir %s --sequence '2b' --gain %d" % (outdir,args.pag))
os.chdir(outdir)
t=g.glob('UNKNOWN*.fits')
for j in range(0,len(t)):
	os.system('mv %s BIAS-PAG%d-%04d.fits' % (t[j],args.pag,j))

# flats
os.system('nglights on')
os.system("/home/ops/ngts/imsequence/imsequence --fastcool --temperature -70 --holdtemp --outdir %s --sequence '2i%d' --gain %d" % (outdir,exptime,args.pag))
t=g.glob('UNKNOWN*.fits')
for j in range(0,len(t)):
	os.system('mv %s FLAT-PAG%d-%04d.fits' % (t[j],args.pag,j))

# analyse and calculate the gain + read noise
calculateGainReadNoise(args.pag)
