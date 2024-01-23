import os
import json
import uuid
import datetime
import zipfile
from dataclasses import asdict

import mysql.connector

from conversion.dwd_conversion_old import parse_xml_to_order_info
from models.vila_model.vila_esko_model import OrderInfo


# Step 1: Read the XML file from the file structure
def read_xml_from_structure(structure_path):
    for root, dirs, files in os.walk(structure_path):
        for file in files:
            if file.endswith('.xml'):
                with open(os.path.join(root, file), 'r') as xml_file:
                    return xml_file.read()

# Step 2: Convert XML to JSON
def xml_to_json(xml_content):
    order_info = parse_xml_to_order_info(xml_content)
    return json.dumps(asdict(order_info), indent=4)

# Step 3: Zip the folder
def zip_folder(folder_path, zip_output_path):
    with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                           os.path.join(folder_path, '..')))

# Step 4: Register in MySQL database
def register_in_database(db_config, zip_file_path):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    insert_query = """INSERT INTO processed_orders (uuid, timestamp, zip_file_location) VALUES (%s, %s, %s)"""
    values = (str(uuid.uuid4()), datetime.datetime.now(), zip_file_path)
    cursor.execute(insert_query, values)
    conn.commit()
    cursor.close()
    conn.close()

# Example usage
structure_path = 'E:\SWITCH\DWD_CERM_CONN\F6D9E9C26E/Cimpress_F6D9E9C26E.xml' #file structure path
zip_output_path = 'zipped_files/zipped.zip'       # Replace with your desired zip file path
db_config = {'user': 'root', 'password': 'mike1969', 'host': '127.0.0.1', 'database': 'vila_cerm_resellers'}

xml_content = read_xml_from_structure(structure_path)
json_output = xml_to_json(xml_content)
zip_folder(structure_path, zip_output_path)
register_in_database(db_config, zip_output_path)

