#!/usr/local/python/bin/python
"""
Code to investigate the field rotation spotted between
the PRESURVEY images and the the AG reference image

Process:
    1. Start by getting the reference image - are they solved?
    2. Get a sample of images throughout the season
    3. Display them to compare them for rotation
    4. Check the WCS solutions for rotation

Questions:
    1. Have the reference images been solved with WCS fit?
    2. Do we have a list of apertures from the Transparency code?
    3. Do the findings match up with the Transparency issue?
"""
import pymysql
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
import astropy.units as u


# connect to the different dbs
db_ops = pymysql.connect(host='ngtsdb', db='ngts_ops')
db_pipe = pymysql.connect(host='ngtsdb', db='ngts_pipe')
field_id = 'NG2100-4748'

ops_qry = """SELECT
    a.action_id, night
    FROM
    action_list AS a
    INNER JOIN action_args AS aa
    ON a.action_id=aa.action_id
    WHERE
    arg_key='field' AND
    arg_value='{0:s}'""".format(field_id)
print(ops_qry)

action_id, night = [], []
image_id = defaultdict(list)
with db_ops.cursor() as ops_cur:
    ops_cur.execute(ops_qry)
    for row in ops_cur:
        action_id.append(row[0])
        night.append(Time(row[1], format='iso', scale='utc'))
        print(row)

# now loop over all the actions and get the image_ids and WCS info
