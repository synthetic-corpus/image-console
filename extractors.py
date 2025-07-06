import abc
import zipfile
import tarfile
import os
import shutil

# --- Abstract Base Class ---

class ArchiveExtractor(abc.ABC):
    """
    Abstract Base Class for archive extraction.

    Defines the interface for all archive extractors.
    """

    @abc.abstractmethod
    def extract(self, archive_path: str, destination_path: str):
        """
        Abstract method to extract the contents of an archive.

        This method must be implemented by concrete subclasses.

        Args:
            archive_path (str): The path to the archive file.
            destination_path (str): The directory where contents will be extracted.

        Raises:
            NotImplementedError: If the method is not implemented by a subclass.
            FileNotFoundError: If the archive file does not exist.
            IsADirectoryError: If the archive_path points to a directory.
            Exception: For various extraction-specific errors.
        """
        raise NotImplementedError("Subclasses must implement the 'extract' method.")

    def _ensure_destination_path(self, destination_path: str):
        """
        Ensures the destination directory exists.

        Args:
            destination_path (str): The path to the destination directory.
        """
        os.makedirs(destination_path, exist_ok=True)
        print(f"Ensured destination path: {destination_path}")

# --- Concrete Implementations ---

class ZipExtractor(ArchiveExtractor):
    """
    Concrete implementation for extracting .zip files.
    """

    def extract(self, archive_path: str, destination_path: str):
        """
        Extracts the contents of a .zip file.

        Args:
            archive_path (str): The path to the .zip file.
            destination_path (str): The directory where contents will be extracted.

        Raises:
            FileNotFoundError: If the .zip file does not exist.
            zipfile.BadZipFile: If the .zip file is corrupted or not a valid zip archive.
            Exception: For other unexpected errors during extraction.
        """
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Zip archive not found: {archive_path}")
        if os.path.isdir(archive_path):
            raise IsADirectoryError(f"'{archive_path}' is a directory, not a zip file.")

        self._ensure_destination_path(destination_path)

        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                print(f"Extracting '{archive_path}' to '{destination_path}'...")
                zip_ref.extractall(destination_path)
                print("Zip extraction complete.")
        except zipfile.BadZipFile as e:
            print(f"Error: The file '{archive_path}' is not a valid zip file or is corrupted. {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during zip extraction: {e}")
            raise

class TarExtractor(ArchiveExtractor):
    """
    Concrete implementation for extracting .tar, .tar.gz, .tar.bz2, etc. files.
    """

    def extract(self, archive_path: str, destination_path: str):
        """
        Extracts the contents of a .tar (or compressed tar) file.

        Args:
            archive_path (str): The path to the .tar file.
            destination_path (str): The directory where contents will be extracted.

        Raises:
            FileNotFoundError: If the .tar file does not exist.
            tarfile.ReadError: If the .tar file is corrupted or not a valid tar archive.
            Exception: For other unexpected errors during extraction.
        """
        if not os.path.exists(archive_path):
            raise FileNotFoundError(f"Tar archive not found: {archive_path}")
        if os.path.isdir(archive_path):
            raise IsADirectoryError(f"'{archive_path}' is a directory, not a tar file.")

        self._ensure_destination_path(destination_path)

        try:
            # tarfile automatically detects compression type (gz, bz2, xz)
            with tarfile.open(archive_path, 'r:*') as tar_ref:
                print(f"Extracting '{archive_path}' to '{destination_path}'...")
                tar_ref.extractall(destination_path)
                print("Tar extraction complete.")
        except tarfile.ReadError as e:
            print(f"Error: The file '{archive_path}' is not a valid tar file or is corrupted. {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred during tar extraction: {e}")
            raise

class SevenZExtractor(ArchiveExtractor):
    """
    Placeholder for .7z file extraction.

    Requires an external library like 'py7zr' or a system command-line tool '7z'.
    """

    def extract(self, archive_path: str, destination_path: str):
        """
        Attempts to extract a .7z file.

        Note: This requires an external library (e.g., 'py7zr' via pip install py7zr)
        or calling the '7z' command-line tool via subprocess.
        This implementation only raises an error as it's not part of standard library.

        Args:
            archive_path (str): The path to the .7z file.
            destination_path (str): The directory where contents will be extracted.

        Raises:
            NotImplementedError: Always, as direct .7z extraction is not in standard library.
        """
        print(f"Attempting to extract .7z file: {archive_path}")
        print("Warning: .7z extraction requires an external library (e.g., 'py7zr') or system tool ('7z').")
        raise NotImplementedError(
            "7z extraction is not supported by Python's standard library. "
            "Consider installing 'py7zr' (pip install py7zr) or using 'subprocess' to call the '7z' command-line tool."
        )

class RarExtractor(ArchiveExtractor):
    """
    Placeholder for .rar file extraction.

    Requires an external library like 'rarfile' or a system command-line tool 'unrar'.
    """

    def extract(self, archive_path: str, destination_path: str):
        """
        Attempts to extract a .rar file.

        Note: This requires an external library (e.g., 'rarfile' via pip install rarfile)
        or calling the 'unrar' command-line tool via subprocess.
        This implementation only raises an error as it's not part of standard library.

        Args:
            archive_path (str): The path to the .rar file.
            destination_path (str): The directory where contents will be extracted.

        Raises:
            NotImplementedError: Always, as direct .rar extraction is not in standard library.
        """
        print(f"Attempting to extract .rar file: {archive_path}")
        print("Warning: .rar extraction requires an external library (e.g., 'rarfile') or system tool ('unrar').")
        raise NotImplementedError(
            "RAR extraction is not supported by Python's standard library. "
            "Consider installing 'rarfile' (pip install rarfile) or using 'subprocess' to call the 'unrar' command-line tool."
        )

# --- Factory Function (Optional, for easy instantiation) ---

# --- Factory Function (Optional, for easy instantiation) ---

def get_extractor(file_path_or_name: str) -> ArchiveExtractor:
    """
    Factory function to get the appropriate extractor based on file extension.

    Args:
        file_path_or_name (str): The full file path or file name (e.g., "archive.zip", "/path/to/my/archive.tar.gz").

    Returns:
        ArchiveExtractor: An instance of the concrete extractor class.

    Raises:
        ValueError: If no suitable extractor is found for the given extension.
    """
    extension_map = {
        ".zip": ZipExtractor,
        ".tar": TarExtractor,
        ".gz": TarExtractor,  # For .tar.gz
        ".tgz": TarExtractor, # For .tar.gz
        ".bz2": TarExtractor, # For .tar.bz2
        ".tbz2": TarExtractor, # For .tar.bz2
        ".xz": TarExtractor,  # For .tar.xz
        ".txz": TarExtractor, # For .tar.xz
        ".7z": SevenZExtractor,
        ".rar": RarExtractor,
    }

    # Extract the extension from the file path or name
    _, ext = os.path.splitext(file_path_or_name)
    normalized_ext = ext.lower()

    # Handle compound extensions like .tar.gz, .tar.bz2, .tar.xz
    # os.path.splitext will give .gz for .tar.gz, so we need to check the full name
    if file_path_or_name.lower().endswith('.tar.gz'):
        normalized_ext = '.gz'
    elif file_path_or_name.lower().endswith('.tar.bz2'):
        normalized_ext = '.bz2'
    elif file_path_or_name.lower().endswith('.tar.xz'):
        normalized_ext = '.xz'
    elif file_path_or_name.lower().endswith('.tgz'):
        normalized_ext = '.tgz'
    elif file_path_or_name.lower().endswith('.tbz2'):
        normalized_ext = '.tbz2'
    elif file_path_or_name.lower().endswith('.txz'):
        normalized_ext = '.txz'
    elif file_path_or_name.lower().endswith('.tar'):
        normalized_ext = '.tar'


    extractor_class = None
    # Check for exact match in the map
    if normalized_ext in extension_map:
        extractor_class = extension_map[normalized_ext]
    # Handle the cases where os.path.splitext gives a single extension for a multi-part one
    elif normalized_ext == '.gz' and '.tar.gz' in file_path_or_name.lower():
        extractor_class = TarExtractor
    elif normalized_ext == '.bz2' and '.tar.bz2' in file_path_or_name.lower():
        extractor_class = TarExtractor
    elif normalized_ext == '.xz' and '.tar.xz' in file_path_or_name.lower():
        extractor_class = TarExtractor


    if extractor_class:
        return extractor_class()
    else:
        raise ValueError(f"No extractor found for file type: {file_path_or_name} (derived extension: {normalized_ext})")

# --- Example Usage (for demonstration) ---
if __name__ == "__main__":
    # Create dummy archive files for testing
    test_dir = "test_archives"
    os.makedirs(test_dir, exist_ok=True)

    # Create a dummy zip file
    zip_file_path = os.path.join(test_dir, "test_archive.zip")
    with zipfile.ZipFile(zip_file_path, 'w') as zf:
        zf.writestr("file1.txt", "This is file 1 in the zip.")
        zf.writestr("subdir/file2.txt", "This is file 2 in a subdirectory.")
    print(f"\nCreated dummy zip file: {zip_file_path}")

    # Create a dummy tar.gz file
    tar_gz_file_path = os.path.join(test_dir, "test_archive.tar.gz")
    with tarfile.open(tar_gz_file_path, 'w:gz') as tf:
        # Create dummy files for tar
        with open(os.path.join(test_dir, "tar_file1.txt"), "w") as f:
            f.write("This is file 1 in the tar.")
        tf.add(os.path.join(test_dir, "tar_file1.txt"), arcname="tar_file1.txt")
        # Clean up dummy file
        os.remove(os.path.join(test_dir, "tar_file1.txt"))
    print(f"Created dummy tar.gz file: {tar_gz_file_path}")

    # Define extraction directories
    zip_dest = os.path.join(test_dir, "extracted_zip")
    tar_dest = os.path.join(test_dir, "extracted_tar")
    sevenz_dest = os.path.join(test_dir, "extracted_7z")
    rar_dest = os.path.join(test_dir, "extracted_rar")

    # --- Test Zip Extraction ---
    print("\n--- Testing Zip Extraction ---")
    try:
        # Now passing the full path
        zip_extractor = get_extractor(zip_file_path)
        zip_extractor.extract(zip_file_path, zip_dest)
        print(f"Contents of {zip_dest}: {os.listdir(zip_dest)}")
        print(f"Contents of {os.path.join(zip_dest, 'subdir')}: {os.listdir(os.path.join(zip_dest, 'subdir'))}")
    except Exception as e:
        print(f"Zip extraction failed: {e}")

    # --- Test Tar.gz Extraction ---
    print("\n--- Testing Tar.gz Extraction ---")
    try:
        # Now passing the full path
        tar_extractor = get_extractor(tar_gz_file_path)
        tar_extractor.extract(tar_gz_file_path, tar_dest)
        print(f"Contents of {tar_dest}: {os.listdir(tar_dest)}")
    except Exception as e:
        print(f"Tar.gz extraction failed: {e}")

    # --- Test 7z Extraction (Expected to fail/raise NotImplementedError) ---
    print("\n--- Testing 7z Extraction ---")
    dummy_7z_path = os.path.join(test_dir, "dummy.7z")
    with open(dummy_7z_path, 'w') as f: # Create a dummy file to simulate a .7z
        f.write("Not a real 7z file content")
    try:
        # Now passing the full path
        sevenz_extractor = get_extractor(dummy_7z_path)
        sevenz_extractor.extract(dummy_7z_path, sevenz_dest)
    except NotImplementedError as e:
        print(f"7z extraction correctly raised NotImplementedError: {e}")
    except Exception as e:
        print(f"Unexpected error during 7z test: {e}")
    finally:
        if os.path.exists(dummy_7z_path):
            os.remove(dummy_7z_path)


    # --- Test Rar Extraction (Expected to fail/raise NotImplementedError) ---
    print("\n--- Testing Rar Extraction ---")
    dummy_rar_path = os.path.join(test_dir, "dummy.rar")
    with open(dummy_rar_path, 'w') as f: # Create a dummy file to simulate a .rar
        f.write("Not a real rar file content")
    try:
        # Now passing the full path
        rar_extractor = get_extractor(dummy_rar_path)
        rar_extractor.extract(dummy_rar_path, rar_dest)
    except NotImplementedError as e:
        print(f"Rar extraction correctly raised NotImplementedError: {e}")
    except Exception as e:
        print(f"Unexpected error during rar test: {e}")
    finally:
        if os.path.exists(dummy_rar_path):
            os.remove(dummy_rar_path)


    # --- Clean up dummy files and directories ---
    print("\n--- Cleaning up test directories ---")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
        print(f"Removed test directory: {test_dir}")
