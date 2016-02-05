import pymysql, sys
import numpy as np
import argparse as ap
import matplotlib.pyplot as pl
from datetime import datetime, timedelta

def argParse():
	parser=ap.ArgumentParser(description='Script to the weather from a given night')
	parser.add_argument("night", help="night to plot weather from (e.g. 2016-01-01)")
	parser.add_argument("n_nights", type=int,help="night to plot weather from (e.g. 2016-01-01)")
	return parser.parse_args()

def setDatetime(indate,n_nights):
	try:
		y,m,d=indate.split('-')
	except ValueError:
		print "Wrong date format. Need YYYY-MM-DD. Trying to convert the date :)"
		if len(indate) != 8:
			print "OK, the date is not even in YYYYMMDD format, I quit!"
			sys.exit(1)
		else:
			y=indate[:4]
			m=indate[4:6]
			d=indate[6:8]
			print "%s --> %s-%s-%s Successful!" % (indate,y,m,d)
	t1=datetime(year=int(y),month=int(m),day=int(d),hour=12,minute=0,second=0)
	t2=t1+timedelta(days=n_nights)
	return t1.strftime('%Y-%m-%dT%H:%M:%S'),t2.strftime('%Y-%m-%dT%H:%M:%S')

args=argParse()
pl.rcParams.update({'font.size': 22})
t1,t2=setDatetime(args.night,args.n_nights)

db=pymysql.connect(host='ds',db='ngts_ops')
# weather
qry="SELECT bucket,humidity,pressure,temperature,dewpoint,wind_speed_avg,wind_dir_avg FROM weather_log WHERE tsample BETWEEN '%s' AND '%s'" % (t1,t2)
with db.cursor() as cur:
	cur.execute(qry)
	n=cur.rowcount
	bucket=np.empty(n)
	humidity=np.empty(n)
	pressure=np.empty(n)
	temperature=np.empty(n)
	dewpoint=np.empty(n)
	wind_speed_avg=np.empty(n)
	wind_dir_avg=np.empty(n)
	i=0
	for row in cur:
		bucket[i]=float(row[0])
		humidity[i]=float(row[1])
		pressure[i]=float(row[2])
		temperature[i]=float(row[3])
		dewpoint[i]=float(row[4])
		wind_speed_avg[i]=float(row[5])
		wind_dir_avg[i]=float(row[6])	
		i+=1
# LDR
qry2="SELECT bucket,ldr FROM cloudwatcher WHERE tsample BETWEEN '%s' AND '%s'" % (t1,t2)
with db.cursor() as cur:
	cur.execute(qry2)
	n2=cur.rowcount
	bucket2=np.empty(n2)
	ldr=np.empty(n2)
	i=0
	for row in cur:
		bucket2[i]=float(row[0])
		ldr[i]=float(row[1])
		i+=1
# sky temp
qry3="SELECT bucket,sky_temp_c FROM cloudwatcher WHERE tsample BETWEEN '%s' AND '%s'" % (t1,t2)
with db.cursor() as cur:
	cur.execute(qry3)
	n3=cur.rowcount
	bucket3=np.empty(n3)
	sky_temp=np.empty(n3)
	i=0
	for row in cur:
		bucket3[i]=float(row[0])
		sky_temp[i]=float(row[1])
		i+=1
db.close()

plots = 0
if plots > 0:
	# plots - vertical
	fig,ax = pl.subplots(6,1,figsize=(10, 30), sharex=True)
	ax[0].fill_between(tpoint,30,50,facecolor='lightcoral',linewidth=0.0)
	ax[0].fill_between(tpoint,10,30,facecolor='lightsalmon',linewidth=0.0)
	ax[0].fill_between(tpoint,-0,10,facecolor='lightblue',linewidth=0.0)
	ax[0].fill_between(tpoint,-20,0,facecolor='deepskyblue',linewidth=0.0)
	#ax[0].set_xlim(-24,0)
	#ax[0].set_ylim(-10,40)
	ax[0].set_ylabel('Temp & Dew Pt. (C)')
	ax[0].plot(tpoint,temperature,'k-')
	ax[0].plot(tpoint,dewpoint,'b-')

	ax[1].fill_between(tpoint,20,35,facecolor='lightcoral',linewidth=0.0)
	ax[1].fill_between(tpoint,17.5,20,facecolor='lightsalmon',linewidth=0.0)
	ax[1].fill_between(tpoint,0,17.5,facecolor='palegreen',linewidth=0.0)
	#ax[1].set_xlim(-24,0)
	ax[1].set_ylim(0,30)
	ax[1].set_ylabel('Wind Speed (m/s)')
	ax[1].plot(tpoint,wind_speed_avg,'k-')

	ax[2].fill_between(tpoint,70,100,facecolor='lightcoral',linewidth=0.0)
	ax[2].fill_between(tpoint,65,70,facecolor='lightsalmon',linewidth=0.0)
	ax[2].fill_between(tpoint,0,65,facecolor='palegreen',linewidth=0.0)
	ax[2].set_xlim(-24,0)
	ax[2].set_ylim(0,100)
	ax[2].set_ylabel('Humidity (%)')
	ax[2].plot(tpoint,humidity,'k-')

	ax[3].fill_between(tpoint3,-20,0,facecolor='lightcoral',linewidth=0.0)
	ax[3].fill_between(tpoint3,-25,-20,facecolor='lightsalmon',linewidth=0.0)
	ax[3].fill_between(tpoint3,-30,-25,facecolor='lightblue',linewidth=0.0)
	ax[3].fill_between(tpoint3,-60,-30,facecolor='deepskyblue',linewidth=0.0)
	ax[3].set_xlim(-24,0)
	ax[3].set_ylim(-60,0)
	ax[3].set_ylabel('Sky Temp (C)')
	ax[3].plot(tpoint3,sky_temp,'k-')

	ax[4].fill_between(tpoint2,200,800,facecolor='lightgrey',linewidth=0.0)
	ax[4].fill_between(tpoint2,800,1200,facecolor='darkgrey',linewidth=0.0)
	ax[4].set_xlim(-24,0)
	ax[4].set_ylim(0,1100)
	ax[4].set_ylabel('LDR')
	ax[4].plot(tpoint2,ldr,'k-')

	ax[5].plot(tpoint,(pressure-0.76)*1000,'k-')
	ax[5].set_xlim(-24,0)
	ax[5].set_ylabel('Pressure (+760 mbar)')
	ax[5].set_xlabel('Hours ago')

	pl.subplots_adjust(hspace=0.07)
	pl.savefig('/home/ops/ngts/prism/monitor/img/current_weather.png',bbox_inches='tight')