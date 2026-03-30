from db import cursor, conn

def create_table():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS gst_data (
        id SERIAL PRIMARY KEY,
        service TEXT,
        gst_rate FLOAT
    )
    """)
    conn.commit()


def insert_data(data):
    for item in data:
        cursor.execute(
            "INSERT INTO gst_data (service, gst_rate) VALUES (%s, %s)",
            (item["service"], item["gst_rate"])
        )
    conn.commit()