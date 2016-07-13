#!/usr/local/python/bin/python
"""
Code to grab the CD matrices from a field's
images and look for rotation

Look at how astrometry.net calculates the rotation
"""
import math
import pymysql
from collections import defaultdict
import numpy as np
import matplotlib.pyplot as plt
from astropy.time import Time
import astropy.units as u

def fitQuad(x, y):
    """
    Generic function to fit 2D polynomial
    to time series data
    """
    xn = np.linspace(x.min(), x.max(), 100)
    coeffs = np.polyfit(x,y,2)
    besty = np.polyval(coeffs, xn)
    return xn, besty

def getSurveyFields():
    """
    Code to grab all the survey fields to check for rotation
    """
    pass

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
times = np.array(times)
cd11 = np.array(cd11)
cd12 = np.array(cd12)
cd21 = np.array(cd21)
cd22 = np.array(cd22)

# make the x axis easier to plot
times = times - times[0]

# work out the rotation from the CD matrices
rot11 = np.arccos(np.radians(cd11/cdelta))
rot12 = np.arcsin(np.radians(cd12/cdelta))
rot21 = np.arcsin(np.radians(cd21/cdelta))
rot22 = np.arccos(np.radians(cd22/cdelta))

# fit the data
#tcd11, cd11_fit = fitQuad(times, rot11)
#tcd12, cd12_fit = fitQuad(times, rot12)
#tcd21, cd21_fit = fitQuad(times, rot21)
#tcd22, cd22_fit = fitQuad(times, rot22)

# set up a figure for plotting
fig=plt.figure(1,figsize=(15,15))
ax11=plt.subplot2grid((4,4),(0,0),colspan=2,rowspan=2)
ax12=plt.subplot2grid((4,4),(0,2),colspan=2,rowspan=2, sharex=ax11)
ax21=plt.subplot2grid((4,4),(2,0),colspan=2,rowspan=2, sharex=ax11)
ax22=plt.subplot2grid((4,4),(2,2),colspan=2,rowspan=2, sharex=ax11)
ax11.plot(times, rot11-np.median(rot11), 'k.')# tcd11, cd11_fit, 'r-')
ax11.set_title('CD1_1 Rot')
ax11.set_ylabel('Rot - median(rot)')
ax12.plot(times, rot12-np.median(rot12), 'k.') # tcd12, cd12_fit, 'r-')
ax12.set_title('CD1_2 Rot')
ax21.plot(times, rot21-np.median(rot21), 'k.') # tcd21, cd21_fit, 'r-')
ax21.set_title('CD2_1 Rot')
ax21.set_ylabel('Rot - median(rot)')
ax21.set_xlabel('Days since day 0')
ax22.plot(times, rot22-np.median(rot22), 'k.') # tcd22, cd22_fit, 'r-')
ax22.set_title('CD2_2 Rot')
ax22.set_xlabel('Days since day 0')


fig=plt.figure(2,figsize=(15,15))
axn11=plt.subplot2grid((4,4),(0,0),colspan=2,rowspan=2)
axn12=plt.subplot2grid((4,4),(0,2),colspan=2,rowspan=2, sharex=axn11)
axn21=plt.subplot2grid((4,4),(2,0),colspan=2,rowspan=2, sharex=axn11)
axn22=plt.subplot2grid((4,4),(2,2),colspan=2,rowspan=2, sharex=axn11)
axn11.plot(times, cd11, 'k.')
axn11.set_title('CD1_1')
axn11.set_ylabel('Rot - median(rot)')
axn12.plot(times, cd12, 'k.')
axn12.set_title('CD1_2')
axn21.plot(times, cd21, 'k.') 
axn21.set_title('CD2_1')
axn21.set_ylabel('Rot - median(rot)')
axn21.set_xlabel('Days since day 0')
axn22.plot(times, cd22, 'k.')
axn22.set_title('CD2_2')
axn22.set_xlabel('Days since day 0')

plt.show()
