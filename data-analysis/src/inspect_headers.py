import zipfile
import sys
import os
import io

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

def inspect_zip(year):
    filename = f"microdados_censo_escolar_{year}.zip"
    filepath = os.path.join(DATA_DIR, filename)
    
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    print(f"--- Inspecting {filename} ---")
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            all_files = z.namelist()
            print(f"All files in zip: {all_files}")
            csv_files = [f for f in all_files if f.lower().endswith('.csv')]
            print(f"Found CSVs: {csv_files}")
            
            if csv_files:
                # Read first line of the first CSV
                with z.open(csv_files[0]) as f:
                    # Read as bytes first to check for utf-8 vs latin1
                    first_line = f.readline()
                    print(f"Raw first line (bytes): {first_line[:100]}...") 
                    
                    try:
                        decoded = first_line.decode('latin1')
                        print(f"Decoded (latin1): {decoded[:200]}")
                        headers = decoded.strip().split(';')
                        print(f"Split headers (delimiter ';'): {headers[:20]}") # Show first 20
                        
                        print(f"Total headers: {len(headers)}")
                        
                        # Check for Special Education / AEE
                        esp_keywords = ['ESP', 'AEE']
                        esp_headers = [h for h in headers if any(k in h for k in esp_keywords)]
                        print(f"Found Special Ed headers: {esp_headers}")

                        # Print ALL QT headers
                        qt_headers = [h for h in headers if 'QT_' in h]
                        print(f"All QT headers: {qt_headers}")
                        
                    except Exception as e:
                        print(f"Error decoding: {e}")

    except Exception as e:
        print(f"Error reading zip: {e}")

if __name__ == "__main__":
    inspect_zip('2021')
    inspect_zip('2022')
    inspect_zip('2023')
