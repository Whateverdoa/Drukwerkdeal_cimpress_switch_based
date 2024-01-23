import os
import shutil
import json
import xml.etree.ElementTree as ET
import zipfile
from dataclasses import asdict
from pathlib import Path

from conversion.dwd_conversion import parse_xml_to_order_info
from mysql_connect.sql_connect import register_in_database

db_config = {'user': 'root', 'password': 'mike1969', 'host': '127.0.0.1', 'database': 'vila_cerm_resellers'}



import os
import shutil
import json
import zipfile
import mysql.connector
from datetime import datetime
import xml.etree.ElementTree as ET
from dataclasses import asdict

# Assuming parse_xml_to_order_info and OrderInfo are defined in your script

def find_first_subfolder(folder_path):
    for item in os.listdir(folder_path):
        full_path = os.path.join(folder_path, item)
        if os.path.isdir(full_path):
            return full_path
    return None

def extract_pdf_files(subfolder_path, target_folder):
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    pdf_files_extracted = 0
    for file in os.listdir(subfolder_path):
        if file.lower().endswith('.pdf'):
            shutil.copy(os.path.join(subfolder_path, file), target_folder)
            pdf_files_extracted += 1
            if pdf_files_extracted == 2:
                break

def read_xml_and_convert_to_json(xml_file_path, target_folder, json_file_name):
    with open(xml_file_path, 'r', encoding="utf-8" ) as xml_file:
        xml_content = xml_file.read()

    order_info = parse_xml_to_order_info(xml_content)
    json_output = json.dumps(asdict(order_info), indent=4)

    json_file_path = os.path.join(target_folder, json_file_name)
    with open(json_file_path, 'w') as f:
        f.write(json_output)

def zip_folder(folder_path, zip_output_path):
    with zipfile.ZipFile(zip_output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                           os.path.join(folder_path, '..')))


def read_json_file(file_path: Path):
    with open(file_path, 'r') as file:
        return file.read()


# folder_name = os.path.basename(os.path.normpath(original_folder))
# new_folder_path = os.path.join(new_location, folder_name)
#
# subfolder_path = find_first_subfolder(original_folder)
# if subfolder_path:
#     extract_pdf_files(subfolder_path, new_folder_path)
#
# xml_file = next((f for f in os.listdir(original_folder) if f.endswith('.xml')), None)
# if xml_file:
#     read_xml_and_convert_to_json(os.path.join(original_folder, xml_file), new_folder_path, f"{folder_name}.json")
#
# # Zip the new folder
#     zip_output_path = os.path.join(new_location, f"{folder_name}.zip")
#     zip_folder(new_folder_path, zip_output_path)
#
#     jsonfile = new_folder_path + '/' + folder_name + '.json'

    # Register in the database
    # register_in_database(db_config,
    #                      folder_name,
    #                      zip_output_path,
    #                      read_json_file(jsonfile))

