"""
Script to get the shutter counts for NGTS
"""
import pymysql

def getLabPedestal(camera_id):
    """
    Get the initial shutter pedestal
    """
    qry2 = """
        SELECT gva, leicester
        FROM shutter_history
        WHERE camera_id = {}
        """.format(camera_id)
    with db.cursor() as cur2:
        cur2.execute(qry2)
        for row2 in cur2:
            try:
                gva = int(row2[0])
            except TypeError:
                gva = 0
            try:
                leicester = int(row2[1])
            except TypeError:
                leicester = 0
            return gva, leicester

def updateImageCount(camera_id, shutter_id, n_images):
    """
    Update the total number of images for
    the currently active shutters
    """
    qry3 = """
        UPDATE camera_shutter_count
        SET n_images = {}
        WHERE camera_id = {}
        AND shutter_id = {}
        """.format(n_images, camera_id, shutter_id)
    with db.cursor() as cur3:
        cur3.execute(qry3)
        db.commit()

if __name__ == '__main__':
    db = pymysql.connect(host='ds', db='ngts_ops')
    qry = """
        SELECT riml.camera_id,shutter_id,count(*)
        FROM raw_image_list as riml
        INNER JOIN camera_shutter_count as csc
        ON riml.camera_id = csc.camera_id
        WHERE csc.active = 1 AND
        riml.bias_mean_adu<5000 AND 
        riml.image_type NOT IN ('BIAS','DARK') AND
        riml.start_time_utc > csc.start_date
        GROUP BY riml.camera_id;
        """
    counts = {}
    with db.cursor() as cur:
        cur.execute(qry)
        for row in cur:
            camera_id = int(row[0])
            shutter_id = int(row[1])
            counts[camera_id] = int(row[2])
            if shutter_id < 13:
                gva, leicester = getLabPedestal(camera_id)
                counts[camera_id] = counts[camera_id] + gva + leicester
            print('{} {} {}'.format(camera_id, counts[camera_id], shutter_id))
            updateImageCount(camera_id, shutter_id, counts[camera_id])
