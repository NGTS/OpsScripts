"""
Get the season RMS using the image IDs of the reference
images as a cross match
"""
import pymysql
import numpy as np

# pylint: disable=invalid-name

if __name__ == "__main__":
    refs = ['80520150922062822', '80520160114005454',
            '80520160114005520', '80520160316004726']
    qry = """
        SELECT x_error, y_error
        FROM autoguider_log
        WHERE ref_image_id IN
            ({})
        """.format(','.join(refs))
    with pymysql.connect(host='10.2.5.32', db='ngts_ops') as cur:
        cur.execute(qry)
        results = cur.fetchall()
    x_error = np.zeros(len(results))
    y_error = np.zeros(len(results))
    for row in results:
        x_error = float(row[0])
        y_error = float(row[1])
    print('RMS X: {:.4f}\tRMS Y: {:.4f}'.format(np.std(x_error),
                                                np.std(y_error)))
