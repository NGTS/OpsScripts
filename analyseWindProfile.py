#!/usr/local/python/bin/python
#
# script to plot the CDF wind speed at paranal
#

import pymysql
import datetime as dt
import matplotlib.pyplot as pl
import numpy as np

t2=dt.datetime.utcnow()
t1=t2-dt.timedelta(days=365)

db=pymysql.connect(host='ds',db='ngts_ops')
qry="SELECT wind_speed_avg,wind_speed_max FROM weather_log WHERE tsample between \'%s\' and \'%s\'" % (t1,t2)
avg,mx=[],[]
with db.cursor() as cur:
	cur.execute(qry)
	for row in cur:
		avg.append(row[0])
		mx.append(row[1])
avg=np.array(avg)
mx=np.array(mx)

for i in range(0,31):
	n_avg=np.where(avg>i)
	n_mx=np.where(mx>i)
	print "Limit: %d m/s - Average > Limit: %.4f - Max > Limit: %.4f" % (i,len(n_avg[0])/float(len(avg)),len(n_mx[0])/float(len(avg)))
