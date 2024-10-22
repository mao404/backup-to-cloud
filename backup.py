import os
import zipfile
from datetime import datetime
import logging
import jsonschema
import json


def setUpLogger():
    logging.basicConfig(filename="backup.log", level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')


def configSchemaValidator(config):
    schema = {
        "type": "object",
        "properties": {
            "directories": {"type": "array", "items": {"type": "string"}},
            "backup_output_dir": {"type": "string"}
        },
        "required": ["directories", "backup_output_dir"]
    }
    jsonschema.validate(config, schema)


def createBackup(backup_dirs, output_dir):
    try:
        backup_filename = os.path.join(
            output_dir, f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        with zipfile.ZipFile(backup_filename, 'w') as zipf:
            for directory in backup_dirs:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        zipf.write(os.path.join(root, file),
                                   os.path.relpath(os.path.join(root, file),
                                                   os.path.join(directory, '..')))
        logging.info(f"Backup created: {backup_filename}")
        print(f"Backup created: {backup_filename}")
        return backup_filename
    except Exception as e:
        logging.error(f"Error creating backup: {e}")
        print(f"Error creating backup: {e}")
        return None


def loadConfig():
    try:
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError:
        logging.error("config.json file not found.")
        print("config.json file not found.")
        return None
    except json.JSONDecodeError:
        logging.error("Error decoding config.json.")
        print("Error decoding config.json.")
        return None


def main():
    setUpLogger()
    config = loadConfig()
    if not config:
        return
    try:
        configSchemaValidator(config)
    except jsonschema.exceptions.ValidationError as e:
        logging.error(f"Invalid configuration: {e}")
        print(f"Invalid configuration: {e}")
        return

    backup_dirs = config['directories']
    backup_output_dir = config['backup_output_dir']

    backup_file = createBackup(backup_dirs, backup_output_dir)
    if backup_file:
        print("Local backup made succesfully")
    else:
        logging.error("Backup creation failed, aborting S3 upload.")
        print("Backup creation failed.")


if __name__ == "__main__":
    main()
