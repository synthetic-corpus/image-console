########################
# A test of functions  #
########################

import os
import io
import re
import hashlib
from PIL import Image
import numpy as np
import uuid

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

def desaturate_image(image_path):
    """ 
    Desaturate an image and save it to 'results' folder with MD5 hash filename
    
    Args:
        image_path (str): Path to the image file to desaturate
    
    Returns:
        str: Path to the saved desaturated image
    """
    # Open and desaturate the image
    image = Image.open(image_path)
    image = image.convert('L')
    
    # Create results directory if it doesn't exist
    results_dir = 'results'
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
    
    # Calculate MD5 hash of the desaturated image
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_data = img_buffer.getvalue()
    md5_hash = hashlib.md5(img_data).hexdigest()
    
    # Create new filename with MD5 hash and original extension
    original_ext = os.path.splitext(image_path)[1]
    new_filename = f"{md5_hash}{original_ext}"
    new_path = os.path.join(results_dir, new_filename)
    
    # Save the desaturated image
    image.save(new_path)
    
    return new_path

def find_all_files(directory_path):
    """ Finds all the files in directroy via stack """
    folder_stack = [directory_path]
    all_files = []
    folders = 0

    while folder_stack:
        current_folder = folder_stack.pop()
        contents = list_directory_contents(current_folder)

        for item in contents:
            if item[1]:
                folder_stack.append(item[0])
                folders += 1
            else:
                all_files.append(item[0])
                image_object = Image.open(item[0])
                process_image_to_numpy_array(image_object, 100, )

    msg = f'Found {len(all_files)} files in {folders} folders'
    return msg, all_files


def resize_and_pad_image(image_file_object, target_pixels_on_side, background_color=(0, 0, 0)):
    """
    Resizes an image to fit within a square of 'target_pixels_on_side'
    while maintaining its aspect ratio, and adds black (or specified color)
    padding to make it a perfect square.

    Args:
        image_file_object: A PIL.Image.Image object (already opened).
        target_pixels_on_side (int): The desired length (in pixels) of each
                                     side of the square output image.
        background_color (tuple): The RGB tuple (0-255) for the padding color.
                                  Defaults to black (0, 0, 0).

    Returns:
        PIL.Image.Image: A new PIL Image object, resized and padded to a square.
                         Returns None if there's an error.
    """
    try:
        if not isinstance(image_file_object, Image.Image):
            print("Error: Input is not a PIL.Image.Image object. (resize)")
            return None

        original_width, original_height = image_file_object.size

        # Determine the scaling factor
        # We scale based on the LARGER dimension to ensure the whole image fits
        if original_width > original_height:
            scale_factor = target_pixels_on_side / original_width
        else:
            scale_factor = target_pixels_on_side / original_height

        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Resize the image while maintaining aspect ratio
        # Ensure the resized image is in RGB mode for consistent color padding
        resized_img = image_file_object.convert("RGB").resize((new_width, new_height), Image.Resampling.LANCZOS)
        # Using LANCZOS for high-quality downsampling

        # Create a new square image with the background color in RGB mode
        padded_img = Image.new('RGB', (target_pixels_on_side, target_pixels_on_side), background_color)

        # Calculate paste position to center the resized image
        paste_x = (target_pixels_on_side - new_width) // 2
        paste_y = (target_pixels_on_side - new_height) // 2

        # Paste the resized image onto the new background
        padded_img.paste(resized_img, (paste_x, paste_y))

        return padded_img

    except Exception as e:
        print(f"An error occurred during resizing and padding: {e}")
        return None

def process_image_to_numpy_array(image_file_object, target_pixels_on_side=64, grayscale=False):
    """
    Takes an image file object and converts it into a preprocessed NumPy array.
    This version uses the separate `resize_and_pad_image` function and
    allows the user to specify whether to grayscale the image.

    Args:
        image_file_object: A PIL.Image.Image object (already opened).
        target_pixels_on_side (int): The desired length (in pixels) of each
                                     side of the square output image.
                                     Defaults to 64.
        grayscale (bool): If True, converts the image to grayscale AFTER padding.
                          If False (default), keeps the original color channels.

    Returns:
        numpy.ndarray: A flattened (1D) NumPy array of the preprocessed image.
                       Pixel values will be scaled to the range [0, 1].
                       Returns None if there's an error processing the image.
    """
    try:
        # Step 1: Resize and pad the image.
        # The padding function now always returns an RGB image for consistency
        padded_img = resize_and_pad_image(image_file_object, target_pixels_on_side)
        if padded_img is None:
            return None # Propagate error from padding function

        # Step 2: Convert to grayscale if specified
        if grayscale:
            padded_img = padded_img.convert('L') # 'L' mode for grayscale
        # If grayscale is False, the image remains in its original padded RGB mode

        save_image(padded_img, 'results')
        # Step 3: Convert PIL Image to NumPy array
        img_array = np.array(padded_img)

        # Step 4: Rescale pixel values to 0-1
        img_array = img_array / 255.0

        # Step 5: Flatten the array
        flattened_img = img_array.flatten()
        save_numpy_array(flattened_img, 'vectors')
        return flattened_img

    except Exception as e:
        print(f"An error occurred during image processing: {e}")
        return None

def save_image(image_object, file_path):
    """
    Saves a PIL.Image.Image object to a specified file path.

    Args:
        image_object: The PIL.Image.Image object to save.
        file_path (str): The relative or absolute path to save the image to.
                         The file format is determined by the file extension.
                         e.g., 'output_image.png', 'folder/test.jpg'
    """
    try:
        if not isinstance(image_object, Image.Image):
            print("Error: Input is not a PIL.Image.Image object. Cannot save.")
            return

        # Ensure the directory exists
        img_buffer = io.BytesIO()
        image_object.save(img_buffer, format='PNG')
        img_data = img_buffer.getvalue()
        md5_hash = hashlib.md5(img_data).hexdigest()
        file_path = f"{file_path}/{md5_hash}.png"
        dir_name = os.path.dirname(file_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Created directory: {dir_name}")

        image_object.save(file_path)
        print(f"Image successfully saved to: {file_path}")
    except Exception as e:
        print(f"An error occurred while saving the image: {e}")


def save_numpy_array(numpy_array, output_directory):
    """
    Saves a NumPy array to a .npy file in the specified directory.
    The filename is generated using the MD5 hash of the array's content.

    Args:
        numpy_array (np.ndarray): The NumPy array to save.
        output_directory (str): The relative or absolute path to the directory
                                where the .npy file should be saved.

    Returns:
        str or None: The full path to the saved .npy file if successful, None otherwise.
    """
    try:
        if not isinstance(numpy_array, np.ndarray):
            print("Error: Input is not a NumPy array. Cannot save.")
            return None


        # 2. Construct the full file path with .npy extension
        unique_id = uuid.uuid4().hex
        filename = f"{unique_id}.npy"
        full_file_path = os.path.join(output_directory, filename)

        # 3. Ensure the output directory exists
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)
            print(f"Created directory: {output_directory}")

        # 4. Save the NumPy array to the .npy file
        np.save(full_file_path, numpy_array)

        print(f"NumPy array successfully saved to: {full_file_path}")
        return full_file_path

    except Exception as e:
        print(f"An error occurred while saving NumPy array: {e}")
        return None

output = find_all_files('test-image')
print(output[0])
print(output[1])

