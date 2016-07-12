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

To do:
    1. Get the time for each image for plotting
    2. Make a 2x2 grid of plots for ROTATION defined by
       each of the 4 CD matrix coeffs
"""
import math
import pymysql
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
import astropy.units as u

# connect to the different dbs
db = pymysql.connect(host='ngtsdb', db='ngts_ops')

# globals
field_id = 'NG0409-1941'
cdelta = 4.98
release = 'TEST16'

# store results here
image_id, times, cd11, cd12, cd21, cd22 = [], [], [], [], [], []

qry = """
    SELECT
    wcs.image_id,
    ril.start_time_utc,
    wcs.cd1_1,
    wcs.cd1_2,
    wcs.cd2_1,
    wcs.cd2_2
    FROM
    ngts_pipe.image_wcsfit AS wcs
    INNER JOIN ngts_ops.raw_image_list AS ril
    ON wcs.image_id = ril.image_id
    WHERE
    prod_id
    IN (SELECT
        pp.prod_id
        FROM
        action_list AS a
        INNER JOIN action_args AS aa
        ON a.action_id=aa.action_id
        INNER JOIN ngts_pipe.photpipe_prod AS pp
        ON a.action_id = pp.action_id
        WHERE
        arg_key='field' AND
        arg_value='{0:s}' AND
        tag='{1:s}')
    """.format(field_id,release)

with db.cursor() as cur:
    length = cur.execute(qry)
    for row in cur:
        if row[2] and row[3] and row[4] and row[5]:
            image_id.append(row[0])
            times.append(Time(row[1], format='datetime', scale='utc').jd)
            cd11.append(row[2])
            cd12.append(row[3])
            cd21.append(row[4])
            cd22.append(row[5])

# make numpy arrays
cd11 = np.array(cd11)
cd12 = np.array(cd12)
cd21 = np.array(cd21)
cd22 = np.array(cd22)

# set up a figure for plotting
fig=plt.figure(1,figsize=(15,15), sharex=True)
ax11=plt.subplot2grid((4,4),(0,0),colspan=2,rowspan=2)
ax12=plt.subplot2grid((4,4),(0,2),colspan=2,rowspan=2)
ax21=plt.subplot2grid((4,4),(2,0),colspan=2,rowspan=2)
ax22=plt.subplot2grid((4,4),(2,2),colspan=2,rowspan=2)
rot11 = np.arccos(np.radians(cd11/cdelta))
rot12 = np.arcsin(np.radians(cd12/cdelta))
rot21 = np.arcsin(np.radians(cd21/cdelta))
rot22 = np.arccos(np.radians(cd22/cdelta))
ax11.plot(times, rot11-np.median(rot11), 'k.')
ax11.title('CD1_1 Rot')
ax12.plot(times, rot12-np.median(rot12), 'k.')
ax12.title('CD1_2 Rot')
ax21.plot(times, rot21-np.median(rot21), 'k.')
ax21.title('CD2_1 Rot')
ax22.plot(times, rot22-np.median(rot22), 'k.')
ax22.title('CD2_2 Rot')
plt.show()
