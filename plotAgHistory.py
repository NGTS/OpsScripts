#!/usr/local/python/bin/python
"""
Script to plot the AG residuals history
Mainly used for plots for posters etc
"""
import pymysql
import numpy as np
from matplotlib import (
    cycler,
    rc
    )
import matplotlib.pyplot as plt

# pylint: disable=invalid-name
# pylint: disable=redefined-outer-name

camera_id = 802
night1 = '2016-03-01'
night2 = '2016-03-07'

# DATA GLOBALS
DATA_LINE_COLOR = 'black'
DATA_LINE_STYLE = '-'
DATA_LINE_WIDTH = 0.5
MODEL_LINE_COLOR = 'red'
MODEL_LINE_STYLE = '-'
MODEL_LINE_WIDTH = 0.7

# AXES GLOBALS
AXES_LINE_WIDTH = 0.5
AXES_MAJOR_TICK_LENGTH = 4
AXES_MINOR_TICK_LENGTH = AXES_MAJOR_TICK_LENGTH/2.
AXES_XTICK_DIRECTION = 'in'
AXES_YTICK_DIRECTION = 'in'

# FIGURE GLOBALS
ONE_COL_WIDTH = 3.545
TWO_COL_WIDTH = 7.09
DPI = 800

def general():
    """
    General settings for all plot types. Call this first,
    then call any cascading style required
    """
    rc('font', family='Times New Roman', size=5)
    rc('text', color='black', usetex=False)
    rc('figure', dpi=DPI)
    rc('axes',
       xmargin=0.05,
       ymargin=0.05,
       linewidth=AXES_LINE_WIDTH,
       labelsize=7,
       prop_cycle=cycler('color', ['black']))
    rc('axes.formatter', limits=(-4, 4))
    rc('axes.spines', left=True, right=True)
    rc('xtick',
       labelsize=7,
       direction=AXES_XTICK_DIRECTION)
    rc('xtick.major',
       size=AXES_MAJOR_TICK_LENGTH,
       width=AXES_LINE_WIDTH)
    rc('xtick.minor',
       visible=True,
       size=AXES_MINOR_TICK_LENGTH,
       width=AXES_LINE_WIDTH)
    rc('ytick',
       labelsize=7,
       direction=AXES_YTICK_DIRECTION)
    rc('ytick.major',
       size=AXES_MAJOR_TICK_LENGTH,
       width=AXES_LINE_WIDTH)
    rc('ytick.minor',
       visible=True,
       size=AXES_MINOR_TICK_LENGTH,
       width=AXES_LINE_WIDTH)

def one_column():
    """
    Two-column-width plot settings
    """
    rc('figure', figsize=(ONE_COL_WIDTH, (ONE_COL_WIDTH/2)))

def two_column():
    """
    Two-column-width plot settings
    """
    rc('figure', figsize=(TWO_COL_WIDTH, (TWO_COL_WIDTH/2.)*0.66))

def getAgStatistics(camera_id, night1, night2):
    """
    Grab the AG data from the database
    """
    with pymysql.connect(host='10.2.5.32', db='ngts_ops') as cur:
        qry = """
            SELECT
            x_error, y_error, x_delta,
            y_delta, night
            FROM autoguider_log as agl
            INNER JOIN raw_image_list as ril
            ON agl.image_id=ril.image_id
            WHERE ril.camera_id = %s
            AND ril.night >= %s
            AND ril.night <= %s
            """
        qry_args = (camera_id, night1, night2)
        print(qry)
        print(qry_args)
        cur.execute(qry, qry_args)
        results = cur.fetchall()
        x_error = np.empty(len(results))
        y_error = np.empty(len(results))
        x_delta = np.empty(len(results))
        y_delta = np.empty(len(results))
        night = []
        for i, row in enumerate(results):
            x_error[i] = round(float(row[0])/5., 2)
            y_error[i] = round(float(row[1])/5., 2)
            x_delta[i] = round(float(row[2])/5., 2)
            y_delta[i] = round(float(row[3])/5., 2)
            night.append(row[4])
    # find night boundaries
    boundaries, night_str = [], []
    for i in range(0, len(night)-1):
        if night[i+1] != night[i]:
            boundaries.append(i+1)
            night_str.append(night[i].strftime("%d"))

    night_str.append('07')
    boundaries.append(len(night))

    return x_error, y_error, x_delta, y_delta, \
           night, np.array(boundaries), night_str

if __name__ == "__main__":
    general()
    one_column()
    # grab the data, scale the number on the x axis
    scaling_factor = 1000.
    x_error, y_error, x_delta, y_delta, night, \
    boundaries, night_str = getAgStatistics(camera_id, night1, night2)

    ind = np.arange(len(x_error))/1000.
    boundaries = boundaries/1000.
    # set up the plots
    fig, ax = plt.subplots(2, 1, sharex=True)
    # plot the frame to frame error
    ax[0].plot(ind, x_error, 'r.', ind, y_error, 'b.', ms=0.25, marker='.')
    ax[0].set_ylabel('Error (pix)')
    ax[0].legend(('X RMS: %.2f pix' % (np.std(x_error)),
                  'Y RMS: %.2f pix' % (np.std(y_error))),
                 loc='lower right', markerscale=3,
                 fontsize=5, scatterpoints=1,
                 facecolor='white', edgecolor='black')
    ax[0].set_ylim(-1.1, 1.1)
    ax[0].set_xlim(0, max(ind))
    ax[0].yaxis.set_ticks_position('both')
    ax[0].xaxis.set_ticks_position('both')
    # draw night boundaries
    for k in range(0, len(boundaries)):
        ax[0].axvline(boundaries[k], lw=0.5, ls='dashed', color='k')
        ax[0].text(boundaries[k]-1.55, 0.5, night_str[k], fontsize=5)
    # plot the cumulative error
    ax[1].plot(ind, x_delta, 'r.', ind, y_delta, 'b.', ms=0.25, marker='.')
    ax[1].set_ylabel('Correction (pix)')
    for k in range(0, len(boundaries)):
        ax[1].axvline(boundaries[k], lw=0.5, ls='dashed', color='k')
        ax[1].text(boundaries[k]-1.55, 2, night_str[k], fontsize=5)
    ax[1].set_ylim(-16, 6)
    ax[1].set_xlim(0, max(ind))
    ax[1].yaxis.set_ticks_position('both')
    ax[1].xaxis.set_ticks_position('both')
    ax[1].set_xlabel(r'Image number ($\times10^{3}$)')
    plt.subplots_adjust(left=0.13, right=0.98, top=0.97,
                        bottom=0.19, hspace=0.05)
    fig.savefig('AgResiduals_802_March2016.png')
