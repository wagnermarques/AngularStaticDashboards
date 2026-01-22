import requests
import os

def download_file(url, dest_path, verify_ssl=True):
    """
    Downloads a file from a URL to a destination path with a progress indicator.
    """
    if os.path.exists(dest_path):
        print(f"File {dest_path} already exists. Skipping download.")
        return True

    print(f"Downloading {url} to {dest_path}...")
    try:
        response = requests.get(url, stream=True, verify=verify_ssl)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024 * 1024  # 1MB
        
        with open(dest_path, 'wb') as f:
            downloaded = 0
            for data in response.iter_content(block_size):
                f.write(data)
                downloaded += len(data)
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    print(f"Progress: {percent:.1f}% ({downloaded}/{total_size} bytes)", end='\r')
        
        print(f"\nDownload completed: {dest_path}")
        return True
    except Exception as e:
        print(f"\nFailed to download {url}: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False
