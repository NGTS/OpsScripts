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
boundaries=[]
for i in range(0,len(night)-1):
	if night[i+1] != night[i]:
		boundaries.append(i+1)


fig,ax=plt.subplots(2,1,sharex=True,figsize=(20,10))
ax[0].plot(x_error,'r.',y_error,'b.',ms=1)
ax[0].set_ylabel('AG Error (Pixels)')
ax[0].legend(('X RMS: %.2f pix' % (np.std(x_error)),'Y RMS: %.2f pix' % (np.std(y_error))),loc='upper left')
ax[0].set_ylim(-1,1)
for k in boundaries:
	ax[0].axvline(k,lw=1,ls='dashed',color='k')
ax[1].plot(x_delta,'r.',y_delta,'b.',ms=1)
ax[1].set_ylabel('AG Correction (Pixels)')
for k in boundaries:
	ax[1].axvline(k,lw=1,ls='dashed',color='k')
plt.subplots_adjust(hspace=0.05)
plt.show()