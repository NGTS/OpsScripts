# script to plot a histogram of some images
from astropy.io import fits
import matplotlib.pyplot as pl
from collections import defaultdict
import numpy as np
import glob as g
import pymysql, os

max_vals=defaultdict(list)
mini_survey_dir='/ngts/staging/archive/minisurvey'

db=pymysql.connect(host='ds',db='ngts_ops')
qry="SELECT image_id,camera_id FROM mini_survey WHERE astrometry=1 AND done=1"
rc=1
image_id,camera_id=[],[]
with db.cursor() as cur:
	cur.execute(qry)
	for row in cur:
		image_id.append(row[0])
		camera_id.append(int(row[1]))
db.close()

for i in range(0,len(image_id)):
	with fits.open('%s/IMAGE%s.fits' % (mini_survey_dir,image_id[i])) as h:
		d=np.ravel(h[0].data)
		max_vals[camera_id[i]].append(max(d))
		img_name='%s/IMAGE%s.hist.png' % (mini_survey_dir,image_id[i])
		if os.path.exists(img_name)==False:
			fig,ax=pl.subplots(1,figsize=(10,10))
			ax.hist(d,range(1,67000)[::100])
			ax.set_yscale('log', nonposy='clip')
			fig.savefig(img_name,dpi=200)
		else:
			print('%s exists, skipping...' % (img_name))
		print rc
		rc+=1

# now make a histogram of the max values per camera
c=0
cameras=np.arange(801,813,1)
figm = pl.figure(rc+1,figsize=(15,15))
figm.clf()
for i in cameras:
	ax = figm.add_subplot(4, 3, c+1)	
	ax.set_title(i)
	if i in max_vals:
		ax.hist(max_vals[i],range(20000,67000)[::100])
	c+=1
figm.savefig('%s/saturationSummary.png' % (mini_survey_dir))
