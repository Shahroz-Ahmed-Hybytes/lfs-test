import boto3
import git
import os
import shutil


BUCKET_NAME = 's3testpush'
S3_FOLDER = '/'  # Replace with the S3 folder path

GITHUB_REPO_URL = 'https://github.com/Shahroz-Ahmed-Hybytes/lfs-test.git'  # Replace with your GitHub repository URL'
CLONE_DIR = '/home/shahroz/Documents/tes_lfs_small'  # Replace with the local GitHub clone directory

def pull_github_repo(repo_dir):
    repo = git.Repo(repo_dir)
    repo.remotes.origin.pull()
    print(f'Pulled latest changes from GitHub repository in {repo_dir}')

def download_s3_folder(s3_client, bucket_name, s3_folder, local_dir):
    objects = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=s3_folder)
    for obj in objects.get('Contents', []):
        s3_key = obj['Key']
        local_path = os.path.join(local_dir, s3_key[len(s3_folder):])
        
        # Create directories if they don't exist
        local_folder = os.path.dirname(local_path)
        if not os.path.exists(local_folder):
            os.makedirs(local_folder)
        
        s3_client.download_file(bucket_name, s3_key, local_path)
        print(f'Downloaded {s3_key} from S3 to {local_path}')

if __name__ == '__main__':
    # Use the AWS CLI configured credentials
    s3 = boto3.client('s3')
    
    # Pull changes from GitHub repository
    pull_github_repo(CLONE_DIR)
    print('GitHub repository pulled')
    
    # Download AWS S3 folder
    download_s3_folder(s3, BUCKET_NAME, S3_FOLDER, CLONE_DIR)
    print(f'All files from S3 folder {S3_FOLDER} downloaded to {CLONE_DIR}')
