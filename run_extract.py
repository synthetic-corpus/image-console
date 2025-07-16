########################################
# This is a Class that is an extractor #
# Meant to be run with main()          #
########################################
import os
import re
import uuid
from randomizer import rename
from s3_access import S3Access
import extractors # for edge case of zips within zips

class ArchiveTraverse():
    def __init__(self, local=False, test=True):
        self.local = local
        self.test = test

    @staticmethod
    def detect_archive(path):
        """ For cases of archives within archives"""
        _, ext = os.path.splitext(file_path_or_name)
        normalized_ext = ext.lower()
        if path.lower().endswith('.tar.gz'):
            normalized_ext = '.gz'
        elif path.lower().endswith('.tar.bz2'):
            normalized_ext = '.bz2'
        elif path.lower().endswith('.tar.xz'):
            normalized_ext = '.xz'
        elif path.lower().endswith('.tgz'):
            normalized_ext = '.tgz'
        elif path.lower().endswith('.tbz2'):
            normalized_ext = '.tbz2'
        elif path.lower().endswith('.txz'):
            normalized_ext = '.txz'
        elif path.lower().endswith('.tar'):
            normalized_ext = '.tar'
        if normalized_ext in [
            '.gz','.bz2','.xz','.tgz','.tbz2','.txz','.tar',
            '.rar','.7z','zip']:
            return True
        else:
            return False

    @staticmethod
    def extract_to_stack(job_root, archive_file):
        """ This handles the case of a Zip file 
        Found within the Zip Files...
        @job_root this is found in the Traverse function.
          Intended to extract the contents of the zip
          file to a new folder there.
        """
        save_point = os.path.join(job_root, str(uuid.uuid4()))
        print('Extracting a nested acrhive!')
        extractor = extractors.get_extractor(archive_file)
        extractor.extract(
            archive_path=archive_file, 
            destination_path=save_point)

        return save_point # will be added to stack

    @staticmethod
    def get_file_name(path):
        return path.split('/')[-1]

    @staticmethod
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

    def traverse_path(self, directory):
        """ Just get the files and list them """
        extraction_root = directory
        print(f'Extraction root for this task = ${extraction_root}')
        folder_stack = [directory]
        all_files = []

        while folder_stack:
            current_folder = folder_stack.pop()
            contents = self.list_directory_contents(current_folder)
            for item in contents:
                if item[1]: # if is folder
                    folder_stack.append(item[0])
                else:
                    # handle two cases:
                    # If Compressed, extract to folder and
                    # palce folder in folder_stack
                    if self.detect_archive(item[0]):
                        msg = f'{item[0]} is a an archive! Extracting under ${current_folder}'
                        folder = self.extract_to_stack(extraction_root, item[0])
                        folder_stack.appen(folder)
                    # Is not .jpg, .png, or .jpeg, continue
                    file_name = self.get_file_name(item[0])
                    all_files.append((item[0],file_name))
        for file_tuple in all_files:
            """ file_tuple = (path, filename) """
            bucket = os.environ.get('S3_BUCKET_NAME')
            try:
                with open(file_tuple[0], 'r') as file_object:
                    r_name = rename(file_tuple[1])
                    if self.test:
                        sub = 'dry run only'
                    else:
                        sub = f'storing to s3: {bucket}'
                    msg = f'{file_tuple[1]} becomes {r_name} - {sub}'
                    print(msg)
                    if self.test == False:
                        key = f'upload/{r_name}'
                        s3access = S3Access(bucket)
                        s3access.put_object(key, file_object)
            except Exception as e:
                print(file_tuple)
                print(e)
