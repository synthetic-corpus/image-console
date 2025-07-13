########################################
# This is a Class that is an extractor #
# Meant to be run with main()          #
########################################
import os

from randomizer import rename

class ArchiveExtract():
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
                    if self.test:
                        # Give the file a random name 
                        # and place in s3 uploads.
                        r_name = rename(file_name)
                        print(f'{file_name} randomize to ${r_name}')
                        print(f'{file_name} Will go to s3 from here!')
                    else:
                        print("will save to s3 for real here!")