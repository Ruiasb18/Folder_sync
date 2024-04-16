import os
import shutil
import time
import argparse
import logging
from hashlib import md5

def calculate_md5(file_path):
    hasher = md5()
    with open(file_path, 'rb') as afile:
        buf = afile.read()
        hasher.update(buf)
    return hasher.hexdigest()

def sync_folders(source, replica):
    for dirpath, dirnames, filenames in os.walk(source):
        # Replicate the directory structure
        relative_path = os.path.relpath(dirpath, source)
        target_dir = os.path.join(replica, relative_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            logging.info(f"Directory created: {target_dir}")

        # Copy/update files
        for filename in filenames:
            source_file = os.path.join(dirpath, filename)
            target_file = os.path.join(target_dir, filename)

            if not os.path.exists(target_file) or calculate_md5(source_file) != calculate_md5(target_file):
                shutil.copy2(source_file, target_file)
                logging.info(f"File copied or updated: {target_file}")

    # Remove files and directories not in source
    for dirpath, dirnames, filenames in os.walk(replica, topdown=False):
        for filename in filenames:
            replica_file = os.path.join(dirpath, filename)
            source_file = os.path.join(source, os.path.relpath(replica_file, replica))
            if not os.path.exists(source_file):
                os.remove(replica_file)
                logging.info(f"File deleted: {replica_file}")

        if not os.listdir(dirpath) and dirpath != replica:
            os.rmdir(dirpath)
            logging.info(f"Directory removed: {dirpath}")

def setup_logging(logfile):
    logging.basicConfig(filename=logfile, level=logging.INFO, format='%(asctime)s - %(message)s')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)

def main():
    parser = argparse.ArgumentParser(description="Synchronize two directories.")
    parser.add_argument("source", help="Source directory to synchronize from.")
    parser.add_argument("replica", help="Replica directory to synchronize to.")
    parser.add_argument("--interval", type=int, default=60, help="Time interval for synchronization in seconds.")
    parser.add_argument("--log", default="sync.log", help="Path to log file.")
    args = parser.parse_args()

    setup_logging(args.log)

    while True:
        logging.info("Starting synchronization")
        sync_folders(args.source, args.replica)
        logging.info("Synchronization complete. Waiting for next interval.")
        time.sleep(args.interval)

if __name__ == "__main__":
    main()


#Only error found: If a folder is created in "source" with nothing inside, the folder is created in replica but eliminated after