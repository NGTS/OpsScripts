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

x_error=np.array(x_error)
y_error=np.array(y_error)
x_delta=np.array(x_delta)
y_delta=np.array(y_delta)

fig,ax=plt.subplots(2,1,sharex=True,figsize=(20,10))
ax[0].plot(x_error,'r.',y_error,'b.')
ax[1].plot(x_delta,'r.',y_delta,'b.')
plt.show()