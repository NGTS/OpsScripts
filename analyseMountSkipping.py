#!/usr/local/python/bin/python
import pymysql
import numpy as np

db=pymysql.connect(host='ds',db='ngts_ops')
qry="SELECT x,y FROM autoguider_log WHERE action_id=%d" % (action_id)
x,y=[],[]
with db.cursor() as cur:
	cur.execute(qry)
	for row in cur:
		x.append(row[0])
		y.append(row[1])
x=np.array(x)
y=np.array(y)

nx=np.where(abs(x)>0.5*5)
ny=np.where(abs(y)>0.5*5)

# concatenate + set the two n's to see the total number of points with ag_res > 0.5 pixels
