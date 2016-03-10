# work out the LEDs + parked telescope exptimes for
# each telescope

import os, sys, time
import glob as g
import numpy as np
import argparse as ap
from matplotlib import cm
from astropy.io import fits
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
	biases=g.glob('BIAS-%d-PAG%d*' % (camera_id,pag))
	flats=g.glob('FLAT-%d-PAG%d*' % (camera_id,pag)) 
	# load images, exclude 20 pixel boarder around the edge
	f1=np.array(fits.open(flats[0])[0].data[20:2028,40:2048]).astype(np.float)
	f2=np.array(fits.open(flats[1])[0].data[20:2028,40:2048]).astype(np.float)
	b1=np.array(fits.open(biases[0])[0].data[20:2028,40:2048]).astype(np.float)
	b2=np.array(fits.open(biases[1])[0].data[20:2028,40:2048]).astype(np.float)
	df=f1-f2
	db=b1-b2
	gain = ( (np.average(f1)+np.average(f2)) - (np.average(b1)+np.average(b2)) ) / (  np.std(df)**2 - np.std(db)**2  )
	rn = ( gain * np.std(db) ) / np.sqrt(2.)
	outfile=open('autogain.log','w')
	outfile.write('| *PAG%d* |  |\n' % (pag))
	outfile.write('| F1 Mean | %.2f |\n' % (np.average(f1)))
	outfile.write('| F2 Mean | %.2f |\n' % (np.average(f2)))
	outfile.write('| Gain | %.3f |\n' % (pag,gain))
	outfile.write('| Read Noise | %.3f |\n' % (pag,rn))
	outfile.close()
	# plot
	#fig = pl.figure(1,figsize=(20,10))
	#ax = fig.add_subplot(1, 2, 1, xticks=[], yticks=[])
	#ax.imshow(df,cmap=cm.afmhot,vmin=0.8*np.median(df),vmax=1.2*np.median(df),interpolation=None)
	#ax.set_title('F1 - F2')
	#ax = fig.add_subplot(1, 2, 2, xticks=[], yticks=[])
	#ax.set_title('B1 - B2')
	#ax.imshow(db,cmap=cm.afmhot,vmin=0.8*np.median(db),vmax=1.2*np.median(db),interpolation=None)
	#fig.savefig('autogain-%d-PAG%d.png' % (camera_id,pag),dpi=200)


# exposure times for each pag
pag={}
pag[1]={801:40, 803:40, 804:15, 805:20, 806:10, 808:5, 809:4, 810:40, 811:6, 812:4, 813:10}
pag[2]={801:20, 803:20, 804: 8, 805:20, 806: 5, 808:3, 809:2, 810:20, 811:4, 812:2, 813:5}
pag[4]={801:20, 803:20, 804: 8, 805:20, 806: 5, 808:3, 809:2, 810:20, 811:4, 812:2, 813:5}


try:
	exptime=pag[args.pag][args.camera_id]
except KeyError:
	print "No stored settings for camera_id: %d with PAG: %d" % (args.camera_id,args.pag)
	print "Exiting"
	sys.exit(1)

home=os.getcwd()
outdir='/local/z_jmcc/autogain/pag%d' % (args.pag)
if os.path.exists(outdir) == False:
	print "Making %s" % (outdir)
	os.mkdir(outdir)

os.chdir(outdir)
# look for images first
biases=g.glob('BIAS-%d-PAG%d*' % (args.camera_id,args.pag))
flats=g.glob('FLAT-%d-PAG%d*' % (args.camera_id,args.pag))

if len(biases) >= 2 and len(flats) >= 2:
	print "Found frames, using them..."
else:	 
	print "Taking new frames..."
	# biases
	os.system('nglights off')
	time.sleep(15)
	os.system("/home/ops/ngts/imsequence/imsequence --fastcool --temperature -70 --holdtemp --outdir %s --sequence '2b' --gain %d" % (outdir,args.pag))
	t=g.glob('UNKNOWN*.fits')
	for j in range(0,len(t)):
		os.system('mv %s BIAS-%d-PAG%d-%04d.fits' % (t[j],args.camera_id,args.pag,j))

	# flats
	os.system('nglights on')
	os.system("/home/ops/ngts/imsequence/imsequence --fastcool --temperature -70 --holdtemp --outdir %s --sequence '2i%d' --gain %d" % (outdir,exptime,args.pag))
	t=g.glob('UNKNOWN*.fits')
	for j in range(0,len(t)):
		os.system('mv %s FLAT-%d-PAG%d-%04d.fits' % (t[j],args.camera_id,args.pag,j))

# analyse and calculate the gain + read noise
calculateGainReadNoise(args.pag,args.camera_id)
