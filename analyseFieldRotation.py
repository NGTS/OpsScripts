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
ops_db = pymysql.connect(host='ngtsdb', db='ngts_ops')
pipe_db = pymysql.connect(host='ngtsdb', db='ngts_pipe')

# globals
field_id = 'NG0409-1941'
cdelta = 4.98

# store results here
action_ids, night = [], []
image_ids = defaultdict(list)
start_times = defaultdict(list)
cd_matrix = defaultdict(list)

ops_qry = """SELECT
    a.action_id, night
    FROM
    action_list AS a
    INNER JOIN action_args AS aa
    ON a.action_id=aa.action_id
    WHERE
    arg_key='field' AND
    arg_value='{0:s}'""".format(field_id)
with ops_db.cursor() as ops_cur:
    ops_cur.execute(ops_qry)
    for row in ops_cur:
        action_ids.append(int(row[0]))
        night.append(Time(str(row[1]), format='iso', in_subfmt='date', scale='utc'))

print("Found {0:d} actions for {1:s}".format(len(action_ids), field_id))
# now loop over all the actions and get the image_ids and WCS info
for action in action_ids:
    image_qry = """SELECT
                image_id, start_time_utc
                FROM
                raw_image_list
                WHERE
                action_id={0:d}
                ORDER BY image_id ASC""".format(action)
    # get the image IDs
    with ops_db.cursor() as ops_cur:
        ops_cur.execute(image_qry)
        for row in ops_cur:
            image_ids[action].append(row[0])
            start_times[action].append(Time(row[1], format='datetime', scale='utc'))
            pipe_qry = """SELECT
                        cd1_1, cd1_2, cd2_1, cd2_2
                        FROM
                        image_wcsfit
                        WHERE
                        image_id={0:d}""".format(int(row[0]))

            # now get the CD matrix
            with pipe_db.cursor() as pipe_cur:
                return_length = pipe_cur.execute(pipe_qry)
                if return_length > 0:
                    for pipe_row in pipe_cur:
                        cd_matrix[action].append(list(pipe_row))
                else:
                    print('No images analysed for {0:d}'.format(action))

# stack the CD arrays into one nice numpy array
# transpose for plotting
for action in cd_matrix:
    cd_matrix[action] = np.vstack(cd_matrix[action]).T

# set up a figure for plotting
fig=plt.figure(1,figsize=(15,15))
ax11=plt.subplot2grid((4,4),(0,0),colspan=2,rowspan=2)
ax12=plt.subplot2grid((4,4),(0,2),colspan=2,rowspan=2)
ax21=plt.subplot2grid((4,4),(2,0),colspan=2,rowspan=2)
ax22=plt.subplot2grid((4,4),(2,2),colspan=2,rowspan=2)

for action in cd_matrix:
    rot1_1 = np.acos(np.radians(cd_matrix[action][0]/cdelta))
    rot1_2 = np.asin(np.radians(cd_matrix[action][1]/cdelta))
    rot2_1 = np.asin(np.radians(cd_matrix[action][2]/cdelta))
    rot2_2 = np.acos(np.radians(cd_matrix[action][3]/cdelta))

    # not plot all the rotations in a 2x2 grid
    # 1 rot calc per grid, showing all values over time
    ax11.plot(start_times[action].jd, rot1_1, 'k.')
    ax12.plot(start_times[action].jd, rot1_2, 'k.')
    ax21.plot(start_times[action].jd, rot2_1, 'k.')
    ax22.plot(start_times[action].jd, rot2_2, 'k.')

plt.show()
