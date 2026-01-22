import csv
import os
import zipfile
import json
import glob
import shutil
import io
import urllib.request
import ssl

# Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
OUTPUT_DIR = os.path.join(BASE_DIR, '../../angular-app/src/assets/data_analysis')

DOWNLOAD_URLS = {
    '2021': 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2021.zip',
    '2022': 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2022.zip',
    '2023': 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2023.zip'
}

# Columns of interest based on INEP microdata (aggregated school data)
COLUMNS_INTEREST = ['NU_ANO_CENSO', 'QT_MAT_ESP']

def process_file(file_path):
    print(f"Processing {file_path}...")
    
    if file_path.endswith('.zip'):
        try:
            with zipfile.ZipFile(file_path, 'r') as z:
                # Look for CSVs, usually microdados_ed_basica_YYYY.csv
                csv_files = [f for f in z.namelist() if f.lower().endswith('.csv')]
                
                # Filter out supplements or dictionaries if possible, though usually the main one is the largest.
                # In 2023 there is 'suplemento_cursos_tecnicos_2023.csv'. We want 'microdados_ed_basica_...csv'.
                target_csv = next((f for f in csv_files if 'microdados_ed_basica' in f), csv_files[0] if csv_files else None)

                if not target_csv:
                    print(f"No CSV found in {file_path}")
                    return {}
                
                print(f"Reading {target_csv} inside zip...")
                with z.open(target_csv) as f:
                    # ZipFile.open returns bytes, need to wrap in TextIOWrapper
                    text_file = io.TextIOWrapper(f, encoding='latin1', newline='')
                    return read_and_aggregate(text_file, delimiter=';')
        except Exception as e:
            print(f"Error reading zip {file_path}: {e}")
            return {}
            
    elif file_path.endswith('.csv'):
        try:
            with open(file_path, 'r', encoding='latin1') as f:
                return read_and_aggregate(f, delimiter=';')
        except Exception as e:
            print(f"Error reading csv {file_path}: {e}")
            return {}
    return {}

def read_and_aggregate(file_handle, delimiter=';'):
    reader = csv.DictReader(file_handle, delimiter=delimiter)
    
    headers = reader.fieldnames
    if not headers:
        return {}
        
    year_stats = {} # year -> count
    
    # Check if we have QT_MAT_ESP
    if 'QT_MAT_ESP' not in headers:
        print("Column QT_MAT_ESP not found. This does not appear to be the School Census file with aggregated metrics.")
        return {}

    count_processed = 0
    
    for row in reader:
        count_processed += 1
        year = row.get('NU_ANO_CENSO')
        qt_esp_str = row.get('QT_MAT_ESP', '0')
        
        if not year:
            continue
            
        try:
            qt_esp = int(qt_esp_str)
            if qt_esp > 0:
                year_stats[year] = year_stats.get(year, 0) + qt_esp
        except ValueError:
            pass
            
    print(f"Processed {count_processed} schools/rows.")
    return year_stats

def download_data():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        
    print("Checking for missing data...")
    # Create unverified context to avoid SSL errors in some envs
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for year, url in DOWNLOAD_URLS.items():
        filename = f"microdados_censo_escolar_{year}.zip"
        filepath = os.path.join(DATA_DIR, filename)
        
        if not os.path.exists(filepath):
            print(f"Downloading data for {year} from {url}...")
            print("This may take a while depending on connection speed.")
            try:
                with urllib.request.urlopen(url, context=ctx) as response, open(filepath, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                print(f"Downloaded {filename}")
            except Exception as e:
                print(f"Failed to download {year}: {e}")
                # Try backup or notify
                pass
        else:
            print(f"Data for {year} already exists.")

def main():
    if not os.path.exists(OUTPUT_DIR):
        print(f"Creating output directory: {OUTPUT_DIR}")
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        
    # Attempt download
    download_data()

    final_stats = {} # Year -> Count

    # Look for files
    files = glob.glob(os.path.join(DATA_DIR, '*.zip')) + glob.glob(os.path.join(DATA_DIR, '*.csv'))
    
    if not files:
        print("No files found in data directory.")
        return

    for f in files:
        file_stats = process_file(f)
        for year, count in file_stats.items():
            final_stats[year] = final_stats.get(year, 0) + count

    if final_stats:
        # Sort by year
        sorted_years = sorted(final_stats.keys())
        results = [{"year": y, "student_count": final_stats[y]} for y in sorted_years]
        
        print("Results:", results)

        # Export JSON
        output_file = os.path.join(OUTPUT_DIR, 'summary_stats.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"JSON saved to {output_file}")

        # --- Generate Plotly Chart ---
        try:
            import plotly.graph_objects as go
            import pandas as pd

            df = pd.DataFrame(results)
            
            fig = go.Figure(data=[
                go.Bar(name='Students', x=df['year'], y=df['student_count'])
            ])
            
            fig.update_layout(
                title_text='Student Count per Year',
                xaxis_title='Year',
                yaxis_title='Number of Students'
            )
            
            chart_output_file = os.path.join(OUTPUT_DIR, 'student_count_by_year.html')
            fig.write_html(chart_output_file, full_html=False, include_plotlyjs='cdn')
            print(f"Chart saved to {chart_output_file}")

        except ImportError:
            print("\nPlotly not installed. Skipping chart generation.")
            print("Please run: pip install plotly pandas")
        # --- End Chart Generation ---

    else:
        print("No valid data processed.")
        # Create an empty or dummy json so Angular doesn't crash?
        # Let's save a "no data" state or just empty list
        with open(os.path.join(OUTPUT_DIR, 'summary_stats.json'), 'w') as f:
            json.dump([], f)

if __name__ == "__main__":
    main()
