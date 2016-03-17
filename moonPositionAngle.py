#!/usr/local/python/bin/python
# script to measure the position angle to the moon
from astropy.coordinates import SkyCoord
from astropy import units as u
import numpy as np
import pymysql

db=pymysql.connect(host='ngtsdb',db='ngts_ops')
action_ids=np.array([107845,107922,108010])

for i in action_ids:
	cmd_ra,cmd_dec,moon_ra,moon_dec=[],[],[],[]
	qry="SELECT cmd_ra,cmd_dec,moon_ra,moon_dec FROM raw_image_list WHERE action_id=%d" % (i)
	with db.cursor() as cur:
		cur.execute(qry)
		for row in cur:
			cmd_ra.append(row[0])
			cmd_dec.append(row[1])
			moon_ra.append(row[2])
			moon_dec.append(row[3])
