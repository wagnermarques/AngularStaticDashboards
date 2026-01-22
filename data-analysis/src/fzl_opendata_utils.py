import zipfile
import os
import glob

def extract_zip(zip_path, extract_to):
    """
    Extracts a zip file to a specific directory.
    """
    if not os.path.exists(zip_path):
        print(f"Zip file not found: {zip_path}")
        return False
        
    print(f"Extracting {zip_path} to {extract_to}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_to)
        return True
    except Exception as e:
        print(f"Error extracting zip: {e}")
        return False

def find_files_in_zip(zip_path, pattern):
    """
    Returns a list of files matching a pattern inside a zip file.
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            return [f for f in z.namelist() if pattern.lower() in f.lower()]
    except Exception as e:
        print(f"Error listing zip contents: {e}")
        return []

def get_file_content_from_zip(zip_path, internal_path):
    """
    Reads the content of a file inside a zip without extracting it.
    Returns a file-like object (bytes).
    """
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            return z.read(internal_path)
    except Exception as e:
        print(f"Error reading file from zip: {e}")
        return None
