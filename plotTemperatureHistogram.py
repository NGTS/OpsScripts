"""
Plot a histogram of temps for Andor
"""
import numpy as np
import matplotlib.pyplot as plt
import pymysql

if __name__ == "__main__":
    qry = """
        SELECT wx_temp
        FROM raw_image_list
        WHERE roof_state = 'FULL OPEN'
        AND camera_id=802
        """
    with pymysql.connect(host='ds', db='ngts_ops') as cur:
        cur.execute(qry)
        results = cur.fetchall()
    temp = []
    for row in results:
        temp.append(row[0])
    temp = np.array(temp)
    fig, ax = plt.subplots(1, figsize=(10, 10))
    ax.hist(temp, bins=100)
    ax.set_xlabel('Temperature (degC)')
    ax.set_ylabel('Frequency')
    fig.savefig('802_OperatingTemperatures.png', dpi=300)
