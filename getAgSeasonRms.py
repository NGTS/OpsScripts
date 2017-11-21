"""
Get the season RMS using the image IDs of the reference
images as a cross match
"""
import pymysql
import numpy as np

# pylint: disable=invalid-name

if __name__ == "__main__":
    pix_scale = 4.96
    refs = ['80520150922062822', '80520160114005454',
            '80520160114005520', '80520160316004726']
    qry = """
        SELECT x_error, y_error, quality
        FROM autoguider_log
        WHERE ref_image_id IN ({})
        AND ABS(x_error) < 10 and ABS(y_error) < 10i
        """.format(','.join(refs))
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
