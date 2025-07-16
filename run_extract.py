########################################
# This is a Class that is an extractor #
# Meant to be run with main()          #
########################################
import os
import re
from randomizer import rename
from s3_access import S3Access

class ArchiveTraverse():
    def __init__(self, local=False, test=True):
        self.local = local
        self.test = test

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
        folder_stack = [directory]
        all_files = []

        while folder_stack:
            current_folder = folder_stack.pop()
            contents = self.list_directory_contents(current_folder)
            for item in contents:
                if item[1]:
                    folder_stack.append(item[0])
                else:
                    all_files.append(item[0])
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
