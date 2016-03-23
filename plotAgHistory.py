#!/usr/local/python/bin/python
'''
Script to plot the AG residuals history
Mainly used for plots for posters etc
'''

import pymysql
import numpy as np
import matplotlib.pyplot as plt

camera_id=802

db=pymysql.connect(host='ngtsdb',db='ngts_ops')
qry="SELECT x_error,y_error,x_delta,y_delta,night,start_time_utc FROM autoguider_log INNER JOIN raw_image_list ON autoguider_log.image_id=raw_image_list.image_id WHERE camera_id = %d AND night > 20160301" % (camera_id)
x_error,y_error,x_delta,y_delta,night,start_time_utc=[],[],[],[],[],[]
with db.cursor() as cur:
	cur.execute(qry)
	for row in cur:
		x_error.append(row[0])
		y_error.append(row[1])
		x_delta.append(row[2])
		y_delta.append(row[3])
		night.append(row[4])
		start_time_utc.append(row[5])

# convert to arrays and pixels
x_error=np.array(x_error)/5.
y_error=np.array(y_error)/5.
x_delta=np.array(x_delta)/5.
y_delta=np.array(y_delta)/5.

# find night boundaries
boundaries,night_str=[],[]
for i in range(0,len(night)-1):
	if night[i+1] != night[i]:
		boundaries.append(i+1)
		night_str.append(night[i].strftime("%Y%m%d"))

fig,ax=plt.subplots(2,1,sharex=True,figsize=(20,10))
ax[0].plot(x_error,'r.',y_error,'b.',ms=1)
ax[0].set_ylabel('AG Error (Pixels)')
ax[0].legend(('X RMS: %.2f pix' % (np.std(x_error)),'Y RMS: %.2f pix' % (np.std(y_error))),loc='lower right',markerscale=5,scatterpoints=1)
ax[0].set_ylim(-1,1)
ax[0].set_xlim(0,len(x_error))
for k in range(0,len(boundaries)):
	ax[0].axvline(boundaries[k],lw=1,ls='dashed',color='k')
	ax[0].text(boundaries[k]-2250,0.5,night_str[k],fontsize=12)

ax[1].plot(x_delta,'r.',y_delta,'b.',ms=1)
ax[1].set_ylabel('AG Correction (Pixels)')
for k in range(0,len(boundaries)):
	ax[1].axvline(boundaries[k],lw=1,ls='dashed',color='k')
	ax[1].text(boundaries[k]-2250,2,night_str[k],fontsize=12)
ax[1].set_ylim(-15,5)
ax[1].set_xlim(0,len(x_error))
ax[1].set_xlabel('Image Number')
plt.subplots_adjust(hspace=0.05)
fig.savefig('AgResiduals_802_March2016.png',dpi=300,bbox_inches='tight')
#plt.show()