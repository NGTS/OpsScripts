#!/usr/local/python/bin/python
import pymysql
import matplotlib.pyplot as pl

def get_battery_data(start, finish):
    """
    """
    qry = """
        SELECT
        last_update, north_v2, north_v4,
        south_v1, south_v4
        FROM roof_battery_voltage
        WHERE last_update > %s AND last_update < %s
        """
    qry_args  = (start, finish)
    with pymysql.connect(host='10.2.5.32', db='ngts_ops',
                         cursorclass=pymysql.DictCursor) as cur:
        cur.execute(qry, qry_args)
        results = cur.fetchall()
    return results

if __name__ == "__main__":
    start = "2019-01-01 00:00:00"
    finish = "2019-10-31 23:59:59"
    data = get_battery_data(start, finish)

    time = data['last_update']
    north_1 = data['north_v2']
    north_2 = data['north_v4']
    south_1 = data['south_v1']
    south_2 = data['south_v4']

    fig, ax = plt.subplots(2, figsize=(10, 10), sharex=True)
    ax[0].plot(time, north_1, 'r-')
    ax[0].plot(time, north_2, 'k-')
    ax[1].plot(time, south_1, 'r-')
    ax[1].plot(time, south_2, 'k-')
    fig.savefig('battery_voltage.png', dpi=300)

