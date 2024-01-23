import mysql.connector
from datetime import datetime
import uuid

def register_in_database(db_config, folder_name, zip_file_path, json_data):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Generate a UUID
    folder_uuid = str(uuid.uuid4())

    # SQL query to insert data
    insert_query = """
    INSERT INTO processed_folders (uuid, name, zip_file_path, json_data, timestamp)
    VALUES (%s, %s, %s, %s, %s)
    """

    # Execute the query
    values = (folder_uuid, folder_name, zip_file_path, json_data, datetime.now())
    cursor.execute(insert_query, values)
    conn.commit()
    cursor.close()
    conn.close()


