#!/usr/bin/env python3
import os
import subprocess
import shutil
# Set the threshold size for large files (in MB)
threshold_size = 90
def check_large_files(directory):
    large_files = []
    for foldername, subfolders, filenames in os.walk(directory):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB
            if file_size > threshold_size:
                large_files.append(file_path)
    return large_files
def track_large_files(large_files):
    for file_path in large_files:
        print(f"Tracking large file with LFS: {file_path}")
        subprocess.run(['git', 'lfs', 'track', file_path])
def exclude_large_files(large_files):
    for file_path in large_files:
        print(f"Excluding large file: {file_path}")
        subprocess.run(['git', 'reset', 'HEAD', file_path])
        subprocess.run(['git', 'rm', '--cached', file_path])
def push_to_s3(directory):
    s3_bucket = "s3testpush"
    print(f"Pushing directory to S3: {directory}")
    subprocess.run(['aws', 's3', 'sync', directory, f's3://{s3_bucket}/{directory}'])
def main():
    # Get the root directory of the Git repository
    root_directory = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode().strip()
    # Check for large files
    large_files = check_large_files(root_directory)
    if large_files:
        # Get the unique parent folders containing large files
        parent_folders = {os.path.dirname(file_path) for file_path in large_files}
        # Track large files with LFS
        track_large_files(large_files)
        # Exclude large files from commit
        exclude_large_files(large_files)
        # Push each specific folder to S3
        for folder in parent_folders:
            push_to_s3(folder)
            print(f"Large files excluded, and folder '{folder}' pushed to S3.")
    else:
        print("No large files found.")
if __name__ == "__main__":
    main()




