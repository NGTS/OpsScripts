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
night1 = '20160301'
night2 = '20160316'

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
ONE_COL_WIDTH = 3.46
DPI = 800

def general():
    """
    General settings for all plot types. Call this first,
    then call any cascading style required
    """
    rc('font', family='Times New Roman', size=7)
    rc('text', color='black', usetex=True)
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
    One-column-width plot settings
    """
    rc('figure', figsize=(ONE_COL_WIDTH, ONE_COL_WIDTH))

def getAgStatistics(camera_id, night1, night2):
    """
    Grab the AG data from the database
    """
    with pymysql.connect(host='ds', db='ngts_ops') as cur:
        qry = """
            SELECT
            x_error, y_error, x_delta,
            y_delta, night
            FROM autoguider_log as agl
            INNER JOIN raw_image_list as ril
            ON agl.image_id=.rilimage_id
            WHERE camera_id = %s
            AND night BETWEEN %s AND %s
            """
        cur.execute(qry, (camera_id, night1, night2))
        results = cur.fetchall()
        x_error = np.empty(len(results))
        y_error = np.empty(len(results))
        x_delta = np.empty(len(results))
        y_delta = np.empty(len(results))
        night = np.empty(len(results))
        for i, row in enumerate(results):
            x_error[i] = round(float(row[0])/5., 2)
            y_error[i] = round(float(row[1])/5., 2)
            x_delta[i] = round(float(row[2])/5., 2)
            y_delta[i] = round(float(row[3])/5., 2)
            night[i] = round(float(row[4])/5., 2)
    # find night boundaries
    boundaries, night_str = [], []
    for i in range(0, len(night)-1):
        if night[i+1] != night[i]:
            boundaries.append(i+1)
            night_str.append(night[i].strftime("%Y%m%d"))
    return x_error, y_error, x_delta, y_delta, \
           night, boundaries, night_str

if __name__ == "__main__":
    general()
    one_column()
    x_error, y_error, x_delta, y_delta, night, \
    boundaries, night_str = getAgStatistics(camera_id, night1, night2)
    fig, ax = plt.subplots(2, 1, sharex=True)
    # plot the frame to frame error
    ax[0].plot(x_error, 'r.', y_error, 'b.', ms=1)
    ax[0].set_ylabel('Error (pixels)')
    ax[0].legend(('X RMS: %.2f pix' % (np.std(x_error)),
                  'Y RMS: %.2f pix' % (np.std(y_error))),
                 loc='lower right',
                 markerscale=5,
                 scatterpoints=1)
    ax[0].set_ylim(-1, 1)
    ax[0].set_xlim(0, len(x_error))
    # draw night boundaries
    for k in range(0, len(boundaries)):
        ax[0].axvline(boundaries[k], lw=1, ls='dashed', color='k')
        ax[0].text(boundaries[k]-2250, 0.5, night_str[k], fontsize=16)
    # plot the cumulative error
    ax[1].plot(x_delta, 'r.', y_delta, 'b.', ms=1)
    ax[1].set_ylabel('Cumulative correction (pixels)')
    for k in range(0, len(boundaries)):
        ax[1].axvline(boundaries[k], lw=1, ls='dashed', color='k')
        ax[1].text(boundaries[k]-2250, 2, night_str[k], fontsize=16)
    ax[1].set_ylim(-15, 5)
    ax[1].set_xlim(0, len(x_error))
    ax[1].set_xlabel('Image Number')
    plt.subplots_adjust(hspace=0.05)
    fig.savefig('AgResiduals_802_March2016.png')
