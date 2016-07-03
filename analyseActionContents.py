import pymysql
import numpy as np
db =  pymysql.connect(host='ds', db='ngts_ops')
actions = np.arange(124659,124874,1)
for i in actions:
    with db.cursor() as cur:
        qry = 'SELECT roof_state FROM raw_image_list WHERE action_id={0:d}'.format(i)
        cur.execute(qry)
        roof = []
        for row in cur:
            roof.append(row[0])
    print('Roof stat of action_id {0:d} = {1:s}'.format(i, roof))

