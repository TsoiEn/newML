import mysql.connector
from mysql.connector import Error

def db_cred():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="md",
            password="(hC2T5Hm",
            database="patient_record"
            
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None
