"""
Get the season RMS using the image IDs of the reference
images as a cross match
"""
import argparse as ap
import pymysql
import numpy as np

# pylint: disable=invalid-name

pix_scale = 4.96
refs = {'NGTS-4b': ['80520150922062822', '80520160114005454',
                    '80520160114005520', '80520160316004726'],
        'NGTS-3Ab': ['81220170204024257', '81220160819092321',
                     '81220170130033545']}

def argParse(refs):
    """
    parse the command line arguments
    """
    p = ap.ArgumentParser()
    p.add_argument('target',
                   help='target ID',
                   choices=refs.keys())
    return p.parse_args()

if __name__ == "__main__":
    args = argParse(refs)
    qry = """
        SELECT x_error, y_error, quality
        FROM autoguider_log
        WHERE ref_image_id IN ({})
        AND ABS(x_error) < 50 and ABS(y_error) < 50
        """.format(','.join(refs[args.target]))
    with pymysql.connect(host='10.2.5.32', db='ngts_ops') as cur:
        cur.execute(qry)
        results = cur.fetchall()
    x_error = np.zeros(len(results))
    y_error = np.zeros(len(results))
    for i, row in enumerate(results):
        x_error[i] = float(row[0])/pix_scale
        y_error[i] = float(row[1])/pix_scale
    print('RMS X: {:.4f}\tRMS Y: {:.4f}'.format(np.std(x_error),
                                                np.std(y_error)))
