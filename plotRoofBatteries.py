#!/usr/local/python/bin/python
import pymysql
import matplotlib.pyplot as plt

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
    qry_args = (start, finish)
    with pymysql.connect(host='10.2.5.32', db='ngts_ops',
                         cursorclass=pymysql.cursors.DictCursor) as cur:
        cur.execute(qry, qry_args)
        results = cur.fetchall()
    return results

if __name__ == "__main__":
    start = "2019-01-01 00:00:00"
    finish = "2019-10-31 23:59:59"
    datas = get_battery_data(start, finish)

    time, north_1, north_2, south_1, south_2 = [], [], [], [], []
    for data in datas:
        time.append(data['last_update'])
        north_1.append(data['north_v2'])
        north_2.append(data['north_v4'])
        south_1.append(data['south_v1'])
        south_2.append(data['south_v4'])

    fig, ax = plt.subplots(2, figsize=(10, 10), sharex=True)
    ax[0].plot(time[::500], north_1[::500], 'r-')
    ax[0].plot(time[::500], north_2[::500], 'k-')
    ax[1].plot(time[::500], south_1[::500], 'r-')
    ax[1].plot(time[::500], south_2[::500], 'k-')
    fig.savefig('battery_voltage.png', dpi=300)

