import psycopg2

conn = psycopg2.connect(
    dbname="gst_db",
    user="postgres",
    password="your_password",
    host="localhost",
    port="5432"
)

cursor = conn.cursor()