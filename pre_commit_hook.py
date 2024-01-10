#!/usr/bin/env python3
import os
import subprocess
import shutil
import logging

# Set the threshold size for large files (in MB)
THRESHOLD_SIZE = 90
S3_BUCKET = "s3testpush"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_large_files(directory):
    large_files = []
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB
            if file_size > THRESHOLD_SIZE:
                large_files.append(file_path)
    return large_files

def track_large_files(large_files):
    for file_path in large_files:
        logger.info(f"Tracking large file with LFS: {file_path}")
        subprocess.run(['git', 'lfs', 'track', file_path])

def exclude_large_files(large_files):
    for file_path in large_files:
        logger.info(f"Excluding large file: {file_path}")
        subprocess.run(['git', 'reset', 'HEAD', file_path])
        subprocess.run(['git', 'rm', '--cached', file_path])

def push_to_s3(directory, parent_folders):
    for folder in parent_folders:
        logger.info(f"Pushing folder '{folder}' to S3: {directory}")
        subprocess.run(['aws', 's3', 'sync', os.path.join(directory, folder), f's3://{S3_BUCKET}/{folder}'])

def main():
    try:
        # Get the root directory of the Git repository
        root_directory = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode().strip()
        # Check for large files
        large_files = check_large_files(root_directory)
        if large_files:
            # Get the unique parent folders containing large files
            parent_folders = {os.path.relpath(os.path.dirname(file_path), root_directory) for file_path in large_files}
            # Track large files with LFS
            track_large_files(large_files)
            # Exclude large files from commit
            exclude_large_files(large_files)
            # Push each specific folder to S3
            push_to_s3(root_directory, parent_folders)
            logger.info("Large files excluded and pushed to S3.")
        else:
            logger.info("No large files found.")
    except Exception as e:
        logger.error(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
