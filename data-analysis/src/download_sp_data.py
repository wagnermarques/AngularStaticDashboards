import os
import urllib.request
import csv
import json
import codecs

# Constants
DATA_URL = "https://dados.educacao.sp.gov.br/sites/default/files/microdados_matricula_sp_2024_12.2024.csv"
OUTPUT_DIR = "data-analysis/data"
RAW_FILE = os.path.join(OUTPUT_DIR, "microdados_sp_2024.csv")
JSON_OUTPUT = os.path.join(OUTPUT_DIR, "sp_disability_stats.json")

# Disability Code Mapping (from Dictionary)
DISABILITY_MAP = {
    "0": "SEM DEFICIENCIA",
    "1": "MULTIPLA",
    "2": "CEGUEIRA",
    "3": "BAIXA VISAO",
    "4": "SURDEZ SEVERA OU PROFUNDA",
    "5": "SURDEZ LEVE OU MODERADA",
    "6": "SURDOCEGUEIRA",
    "7": "FISICA-PARALISIA CEREBRAL",
    "8": "FISICA-CADEIRANTE",
    "9": "FISICA-OUTROS",
    "10": "SINDROME DE DOWN",
    "11": "INTELECTUAL",
    "12": "VISAO MONOCULAR",
    "20": "AUTISTA INFANTIL",
    "21": "SINDROME DE ASPERGER",
    "22": "SINDROME DE RETT",
    "23": "TRANSTORNO DESINTEGRATIVO DA INFANCIA",
    "30": "ALTAS HABILIDADES/SUPERDOTACAO"
}

def download_data():
    if os.path.exists(RAW_FILE):
        print(f"File {RAW_FILE} already exists. Skipping download.")
        return

    print(f"Downloading data from {DATA_URL}...")
    try:
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        # Download with progress indication (simple)
        def progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = downloaded * 100 / total_size
                if block_num % 1000 == 0:  # Update every ~8MB
                    print(f"Download progress: {percent:.1f}%", end='\r')
        
        urllib.request.urlretrieve(DATA_URL, RAW_FILE, progress)
        print("\nDownload complete.")
    except Exception as e:
        print(f"Failed to download data: {e}")
        # Clean up partial file
        if os.path.exists(RAW_FILE):
            os.remove(RAW_FILE)
        raise

def process_data():
    print("Processing data...")
    
    # Columns of interest - we need to find their indices
    # We will read the header row first
    
    stats = {}
    
    try:
        # Use latin1 encoding as per usual Brazilian gov data
        with open(RAW_FILE, 'r', encoding='latin1', errors='replace') as f:
            # Check delimiter
            sample = f.read(1024)
            f.seek(0)
            delimiter = ';' if ';' in sample else ','
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            # Verify columns exist
            fieldnames = reader.fieldnames
            if not fieldnames:
                raise Exception("Empty CSV or no header.")
                
            # Normalize field names just in case (strip spaces)
            field_map = {name.strip(): name for name in fieldnames}
            
            mun_col = field_map.get('MUN')
            rede_col = field_map.get('NOMEDEP')
            
            # Find DEF columns
            def_cols = []
            for i in range(1, 11):
                col_name = f"DEF{i}"
                if col_name in field_map:
                    def_cols.append(field_map[col_name])
            
            if not mun_col or not rede_col:
                print(f"Available columns: {list(field_map.keys())}")
                raise Exception("Missing required columns MUN or NOMEDEP")

            print(f"Processing with columns: MUN={mun_col}, DEF={def_cols}")

            count = 0
            for row in reader:
                count += 1
                if count % 100000 == 0:
                    print(f"Processed {count} rows...", end='\r')

                # Check for disability
                has_disability = False
                student_disabilities = []

                for col in def_cols:
                    val = row.get(col, "0")
                    if val and val != "0" and val in DISABILITY_MAP:
                        has_disability = True
                        student_disabilities.append(DISABILITY_MAP[val])
                
                if has_disability:
                    mun = row.get(mun_col, "DESCONHECIDO")
                    if mun not in stats:
                        stats[mun] = {}
                    
                    for d in student_disabilities:
                        if d not in stats[mun]:
                            stats[mun][d] = 0
                        stats[mun][d] += 1
                        
    except Exception as e:
        print(f"Error processing CSV: {e}")
        raise

    # Save to JSON
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)
    
    print(f"\nStats saved to {JSON_OUTPUT}")

if __name__ == "__main__":
    download_data()
    process_data()
