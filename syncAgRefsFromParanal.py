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
    warwick = [line.rstrip() for line in open('ags_at_warwick.txt').readlines()]
    paranal = sorted(g.glob('*.fits'))
    sync = [image for image in paranal if image not in warwick]
