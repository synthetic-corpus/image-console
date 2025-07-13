############################################################
# This file will process a collection of rar, .tz .zip etc #
# And extract their files to a loca drive.                 #
# Then It will move them to the s3 bucket                  #
############################################################

import os
import uuid
import pathlib
import re
import uuid
import shutil
from extractors import get_extractor

# Check first if we're runnin is EC2,
# In which case, use ebs.

if os.path.exists('/mnt/ebs_volume'):
    local_source = None # because we'll use s3
    work_space = os.path('/mnt/ebs_volume')
else:
    local_source = os.path.abspath('root/zips')
    os.makedirs('root/work_space', exist_ok=True)
    work_space = os.path.abspath('root/work_space')
    os.makedirs('root/results', exist_ok=True)
    results = os.path.abspath('root/results')

def list_directory_contents(directory_path):
    """
    List everything within a directory and return a list of tuples.
    
    Args:
        directory_path (str): Path to the directory to list contents of
    
    Returns:
        list: List of tuples, each containing (absolute_path, is_folder_boolean)
    """
    result_list = []
    
    try:
        # Check if the directory exists
        if not os.path.exists(directory_path):
            print(f"Error: Directory '{directory_path}' does not exist.")
            return result_list
        # Check if the path is actually a directory
        if not os.path.isdir(directory_path):
            print(f"Error: '{directory_path}' is not a directory.")
            return result_list
        
        # List all items in the directory
        for item in os.listdir(directory_path):
            pattern = r'\.DS_Store$'  #pattern to be ignored
            if re.search(pattern, item):
                continue
            # Construct the full path to the item
            item_path = os.path.join(directory_path, item)
            abs_item_path = os.path.abspath(item_path)
            
            # Check if it's a directory
            is_folder = os.path.isdir(item_path)
            
            # Create tuple and append to list
            item_tuple = (abs_item_path, is_folder)
            result_list.append(item_tuple)
                
    except PermissionError:
        print(f"Error: Permission denied accessing directory '{directory_path}'")
    except Exception as e:
        print(f"Error: {e}")
    
    return result_list

def get_file_name(path):
    return path.split('/')[-1]

def traverse_path(directory):
    """ Just get the files and list them """
    folder_stack = [directory]
    all_files = []

    while folder_stack:
        current_folder = folder_stack.pop()
        contents = list_directory_contents(current_folder)
        for item in contents:
            if item[1]:
                folder_stack.append(item[0])
            else:
                all_files.append(item[0])
                file_name = get_file_name(item[0])
                print(f'Move or Save to s3 here: {file_name}')
                if not local_source:
                    # Give the file a random name 
                    # and place in s3 uploads.
                    print('Will go to s3 from here!')

if local_source:
    print(local_source)
    # Get a list of all compressed files from a local directory.
    compressed_files = []
    for item in os.listdir(local_source):
        print(item)
        pattern = r'\.DS_Store$'  #pattern to be ignored
        if re.search(pattern, item):
            continue
        # Construct the full path to the item
        path = os.path.join(local_source, item)
        compressed_files.append(path)

    for archive in compressed_files:
        job = uuid.uuid4()
        destination = os.path.join(work_space, str(job))
        print(f'extracting to f{destination}')
        extractor = get_extractor(archive)
        extractor.extract(archive, destination)
        print('Run next functions here')
        traverse_path(destination)
        print(f'completed job ${job}. Deleting temp folder')
        shutil.rmtree(destination)

else:
    print("extracting from an s3 Bucket")
    keys = [] # a list of Keys from the s3 bucket
    for key in keys:
        job = uuid.uuid()
        save_point = os.path.join(work_space, str(job))
        extract_point = os.path.join(save_point, 'output')
        # Todo: Copy the Archive to Save Point
        extractor = get_extractor('archive')
        extractor.extract('archive', extract_point)
        traverse_path(extract_point)
        shutil.rmtree(save_point)