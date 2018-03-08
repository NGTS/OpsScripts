"""
The old rsync of archive copied the ag references
This was stopped and now we must manually sync them
back occassionally. This script works out which need
synced back
"""
import os
import glob as g
import numpy as np

# pylint: disable=invalid-name

if __name__ == "__main__":
    os.chdir('/ngts/autoguider_ref/')
    warwick = np.loadtxt('ags_at_warwick.txt', usecols=[0], unpack=True)
    paranal = sorted(g.glob('*.fits'))
    sync = [image for image in paranal if image not in warwick]
