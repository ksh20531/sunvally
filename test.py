import config
import pymysql
import datetime
import time

# conn = pymysql.connect(host=config.db_host, user=config.db_user, password=config.db_pw, db=config.db_database)
#
# cursor = conn.cursor()
# field = '설악'
# sql = 'SELECT reservation.id,name,code,time,reservation_time,reservation.deleted ' \
#       'FROM golf_reservations AS reservation ' \
#       'JOIN golf_fields AS field ' \
#       'ON reservation.field_id = field.id WHERE name="'+field+'" ' \
#       'AND reservation.deleted = 0 ' \
#       'ORDER BY reservation.id desc;'
# cursor.execute(sql)
# row = cursor.fetchone()
# conn.close()
#
# print(row[4])
