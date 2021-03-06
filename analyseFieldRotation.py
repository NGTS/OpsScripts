#!/usr/local/python/bin/python
"""
Code to grab the CD matrices from a field's
images and look for rotation

Look at how astrometry.net calculates the rotation
"""
import os
import math
from collections import defaultdict
import numpy as np
import pymysql
import matplotlib
matplotlib.use('Agg') # Do not require x forwarding to render static files
import matplotlib.pyplot as plt
from astropy.time import Time

# pylint: disable = invalid-name

# connect to the different dbs
db = pymysql.connect(host='ngtsdb', db='ngts_ops')

# globals
cdelta = 4.98
release = 'CYCLE1706'
filestore = '/home/jmcc/dev/OpsScripts/CDMatrix'

def fitQuad(x, y):
    """
    Generic function to fit 2D polynomial
    to time series data
    """
    xn = np.linspace(x.min(), x.max(), 100)
    coeffs = np.polyfit(x, y, 2)
    besty = np.polyval(coeffs, xn)
    return xn, besty

def getSurveyFields():
    """
    Code to grab all the survey fields to check for rotation
    """
    qry = """
        SELECT
        field,
        camera_id,
        first_night,
        last_night
        FROM
        field_summary
        WHERE
        campaign LIKE '20%'
        """
    cameras = defaultdict(list)
    with db.cursor() as cur:
        cur.execute(qry)
        for row in cur:
            first_night = Time(str(row[2]), format='iso', in_subfmt='date', scale='utc')
            last_night = Time(str(row[3]), format='iso', in_subfmt='date', scale='utc')
            cameras[int(row[1])].append([row[0], first_night, last_night])
    return cameras


def plotCDMatrixFromField(field_id, release, camera_id):
    """
    Code to plot the CD Matrix values for a given field
    """
    outname = "{0:s}-{1:d}-{2:s}.png".format(field_id, camera_id, release)
    outdir = '{0:s}/{1:d}/'.format(filestore, camera_id)
    if not os.path.exists(outdir):
        os.mkdir(outdir)

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
        """.format(field_id, release)

    with db.cursor() as cur:
        length = cur.execute(qry)
        if length > 0:
            for row in cur:
                if row[2] and row[3] and row[4] and row[5]:
                    image_id.append(row[0])
                    times.append(Time(row[1], format='datetime', scale='utc').jd)
                    cd11.append(row[2])
                    cd12.append(row[3])
                    cd21.append(row[4])
                    cd22.append(row[5])
        else:
            print('No CD Matrix data for {0:s}'.format(field_id))
            return

    # make numpy arrays
    times = np.array(times)
    cd11 = np.array(cd11)
    cd12 = np.array(cd12)
    cd21 = np.array(cd21)
    cd22 = np.array(cd22)

    # now extract the rotation from the CD matrix
    rot1 = np.degrees(np.arctan(cd21/cd11))
    rot2 = np.degrees(np.arctan(-cd12/cd22))

    # make the x axis easier to plot
    times = times - times[0]

    # plot
    fig = plt.figure(1, figsize=(15, 15))
    plt.ticklabel_format(style='plain')#, axis='y', scilimits=(0,0))
    ax11 = plt.subplot2grid((6, 4), (0, 0), colspan=2, rowspan=2)
    ax12 = plt.subplot2grid((6, 4), (0, 2), colspan=2, rowspan=2, sharex=ax11)
    ax21 = plt.subplot2grid((6, 4), (2, 0), colspan=2, rowspan=2, sharex=ax11)
    ax22 = plt.subplot2grid((6, 4), (2, 2), colspan=2, rowspan=2, sharex=ax11)
    axr1 = plt.subplot2grid((6, 4), (4, 0), colspan=2, rowspan=2, sharex=ax11)
    axr2 = plt.subplot2grid((6, 4), (4, 2), colspan=2, rowspan=2, sharex=ax11)
    ax11.plot(times, cd11, 'k.')
    ax11.set_title('CD1_1')
    ax11.set_ylabel('')
    ax12.plot(times, cd12, 'k.')
    ax12.set_title('CD1_2')
    ax21.plot(times, cd21, 'k.')
    ax21.set_title('CD2_1')
    ax21.set_ylabel('')
    ax22.plot(times, cd22, 'k.')
    ax22.set_title('CD2_2')
    axr1.plot(times, rot1, 'k.')
    axr1.set_title('Rot 1')
    axr1.set_ylabel('Degrees')
    axr1.set_xlabel('Days since day 0')
    axr2.plot(times, rot2, 'k.')
    axr2.set_title('Rot 2')
    axr2.set_xlabel('Days since day 0')
    fig.savefig('{0:s}{1:s}'.format(outdir, outname))

if __name__ == '__main__':
    cameras = getSurveyFields()
    c = 1
    for i in cameras:
        for j in cameras[i]:
            print('{0:d} Plotting CD Matrix for {1:d} - {2:s}'.format(c, i, j[0]))
            plotCDMatrixFromField(j[0], release, i)
            c += 1
