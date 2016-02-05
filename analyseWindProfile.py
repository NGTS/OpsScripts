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
outdir='/home/ops/ngts/prism/monitor/img'
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
wind=np.arange(0,35,1)
cdf_avg=np.empty(len(wind))
cdf_mx=np.empty(len(wind))
for i in range(0,len(wind)):
	n_avg=np.where(avg>i)
	n_mx=np.where(mx>i)
	cdf_avg[i]=1-(len(n_avg[0])/float(len(avg)))
	cdf_mx[i]=1-(len(n_mx[0])/float(len(avg)))
	print "Limit: %d m/s - Average > Limit: %.4f - Max > Limit: %.4f" % (i,cdf_avg[i],cdf_mx[i])

fig,ax=pl.subplots(1,figsize=(10,10))
ax.plot(wind,cdf_avg,'r-',wind,cdf_mx,'b-')
ax.legend(('average','gust'),loc='upper left')
ax.set_ylabel('CDF Wind Speed')
ax.set_xlabel('Wind Speed (m/s)')
ax.grid(True)
fig.savefig('%s/WindProfile_%s-%s.png' % (outdir,t1.strftime('%Y%m%d'),t2.strftime('%Y%m%d')),dpi=200)