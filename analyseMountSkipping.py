#!/usr/local/python/bin/python
import pymysql
import numpy as np
import argparse as ap

def argParse():
	parser=ap.ArgumentParser(description="Script to analyse the mount skipping frequency")
	parser.add_argument('camera_id',type=int,help="Camera ID to analyse skipping frequency")
	parser.add_argument('night',type=int,help="Night to analyse, e.g. 20160203")
	return parser.parse_args()

args=argParse()
db=pymysql.connect(host='ds',db='ngts_ops')
qry="SELECT image_id,start_time_utc,x_error,y_error,night FROM autoguider_log LEFT JOIN raw_image_list USING (image_id) WHERE camera_id=%d AND night='%s';" % (args.camera_id,args.night)
x,y=[],[]
with db.cursor() as cur:
	cur.execute(qry)
	for row in cur:
		x.append(row[2])
		y.append(row[3])
x=np.array(x)
y=np.array(y)

nx=np.where(abs(x)>0.5*5)
ny=np.where(abs(y)>0.5*5)

# concatenate + set the two n's to see the total number of points with ag_res > 0.5 pixels
