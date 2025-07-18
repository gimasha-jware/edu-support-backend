import mysql.connector
from mysql.connector import Error

conn = None

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Mysql@123'  
    )
    if conn.is_connected():
        print("Connection successful")
except Error as e:
    print("Connection failed:", e)
finally:
    if conn and conn.is_connected():
        conn.close()