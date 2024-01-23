import logging
import os
import shutil
import time
from pathlib import Path

from Paden.paden import original_folder, new_location
from transportation.extract_pdf_and_remap_xml import find_first_subfolder, extract_pdf_files, \
    read_xml_and_convert_to_json, zip_folder
rd /S /Q .git

# Setup logging
logging.basicConfig(filename='process_log.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def process_folders():
    # Collecting all folders in the original directory
    directory_path = Path(original_folder)
    folder_paths = [folder for folder in directory_path.iterdir() if folder.is_dir()]

    if not folder_paths:
        logging.info("No folders to process.")


    for folder in folder_paths:
        folder_name = os.path.basename(os.path.normpath(folder))
        new_folder_path = os.path.join(new_location, folder_name)

        try:
            # Operations on each subfolder
            subfolder_path = find_first_subfolder(folder)
            if subfolder_path:
                extract_pdf_files(subfolder_path, new_folder_path)

            xml_file = next((f for f in os.listdir(folder) if f.endswith('.xml')), None)
            if xml_file:
                read_xml_and_convert_to_json(os.path.join(folder, xml_file), new_folder_path, f"{folder_name}.json")

             # Zip the new folder
            zip_output_path = os.path.join(new_location, f"{folder_name}.zip")
            zip_folder(new_folder_path, zip_output_path)
            logging.info(f"Successfully zipped folder: {new_folder_path}")
            logging.info(f"Successfully zipped to folder: {zip_output_path}")

            try:
                # Delete the new folder after zipping
                shutil.rmtree(new_folder_path)
                logging.info(f"Deleted the new folder after zipping: {new_folder_path}")
            except Exception as e:
                logging.error(f"Failed to delete the new folder after zipping: {new_folder_path} due to: {e}")

            # Delete the original folder after all operations are complete
            shutil.rmtree(folder)
            logging.info(f"Deleted the new folder after zipping:{folder}")

        except Exception as e:
            logging.error(f"Failed to process folder: {new_folder_path} due to: {e}")


    

if __name__ == '__main__':
    while True:
        process_folders()
        time.sleep(5*60)  # Wait for 5 * 60 seconds
        