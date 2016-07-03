import pymysql
import numpy as np
db =  pymysql.connect(host='ds', db='ngts_ops')
actions = np.arange(124659,124874,1)
for i in actions:
    with db.cursor() as cur:
        qry = 'SELECT img_median_cnts FROM raw_image_list WHERE action_id={0:d}'.format(i)
        cur.execute(qry)
        meds = []
        for row in cur:
            meds.append(float(row[0]))
        meds = np.array(meds)
    print('Median of action_id {0:d} = {1:.2f}'.format(i, np.median(meds))

