#!/usr/local/python/bin/python
# script to measure the position angle to the moon
from astropy.coordinates import SkyCoord
from astropy import units as u
from collections import defaultdict
import numpy as np
import pymysql

db=pymysql.connect(host='ngtsdb',db='ngts_ops')
action_ids=np.array([107845,107922,108010])
pos_dict=defaultdict(list)
meds_dict=defaultdict(list)
for i in action_ids:
	position_angle,cmd_ra,cmd_dec,moon_ra,moon_dec=[],[],[],[],[]
	qry="SELECT cmd_ra,cmd_dec,moon_ra,moon_dec FROM raw_image_list WHERE action_id=%d" % (i)
	with db.cursor() as cur:
		cur.execute(qry)
		for row in cur:
			cmd_ra.append(row[0])
			cmd_dec.append(row[1])
			moon_ra.append(row[2])
			moon_dec.append(row[3])
	obj=SkyCoord(cmd_ra*u.deg,cmd_dec*u.deg,frame='icrs')
	moon=SkyCoord(moon_ra*u.deg,moon_dec*u.deg,frame='icrs')
	for j in range(0,len(obj)):
		position_angle.append(obj[j].position_angle(moon[j]).deg)
	pos_dict[i]=position_angle
	meds_dict[i]=np.median(position_angle)


