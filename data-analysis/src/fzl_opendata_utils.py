import zipfile
import os
import pandas as pd
import numpy as np

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

def fzl_opendata_list_fields_in_dictionary_excel_file(excel_path, output_html_path):
    """
    Open excel file extracted from zip and create a html table listing all fields in the dictionary.
    The excel has labels on line 7 (header=6) and data starting on line 10.
    """
    print(f"Reading dictionary from {excel_path}...")
    try:
        # Read with header at line 7 (index 6)
        # Use first sheet as requested
        df_raw = pd.read_excel(excel_path, sheet_name=0, header=6)
        
        # Identify relevant columns
        cols = df_raw.columns.tolist()
        
        # Columns we want to extract
        target_cols = {
            'N': next((c for c in cols if str(c).strip() == 'N'), None),
            'Nome da Variável': next((c for c in cols if 'nome' in str(c).lower() and 'vari' in str(c).lower()), None),
            'Descrição da Variável': next((c for c in cols if 'desc' in str(c).lower() and 'vari' in str(c).lower()), None),
            'Tipo': next((c for c in cols if 'tipo' in str(c).lower()), None),
            'Categoria': next((c for c in cols if 'categ' in str(c).lower()), None)
        }

        # Filter out keys that weren't found
        found_mapping = {k: v for k, v in target_cols.items() if v is not None}
        
        if not found_mapping.get('Nome da Variável'):
            print("Could not find 'Nome da Variável' column.")
            return []

        # Start from what was line 10. 
        # Header was line 7 (row index 6).
        # Row index 7 is line 8.
        # Row index 8 is line 9.
        # Row index 9 is line 10.
        df_data = df_raw.iloc[3:].copy() # Skip 3 rows after header to reach line 10
        
        # Detect end of data using 'N' column if it exists
        if 'N' in found_mapping:
            n_col = found_mapping['N']
            # Convert N to numeric, and stop at first NaN
            df_data[n_col] = pd.to_numeric(df_data[n_col], errors='coerce')
            # Filter rows where N is a number
            df_data = df_data[df_data[n_col].notnull()]

        # Prepare final display DataFrame
        display_cols = ['Nome da Variável', 'Descrição da Variável', 'Tipo', 'Categoria']
        actual_cols = [found_mapping[c] for c in display_cols if c in found_mapping]
        
        df_display = df_data[actual_cols].copy()
        df_display.columns = [c for c in display_cols if c in found_mapping]
        
        # Clean up variable names for the return list
        variable_names = df_display['Nome da Variável'].dropna().apply(lambda x: str(x).strip().upper()).tolist()

        # Save to HTML
        os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
        df_display.to_html(output_html_path, index=False, classes='table table-striped table-bordered')
        print(f"Dictionary fields table saved to {output_html_path} ({len(df_display)} fields)")
        
        return variable_names
        
    except Exception as e:
        print(f"Error processing dictionary excel: {e}")
        import traceback
        traceback.print_exc()
        return []

def fzl_opendata_detect_duplicate_records(df, fields_to_check, output_html_path, year_label):
    """
    Detect duplicate records based on a list of fields and log them in an html table.
    """
    print(f"Checking for duplicates in {year_label} data...")
    try:
        # Only use fields that actually exist in the DataFrame
        valid_fields = [f for f in fields_to_check if f in df.columns]
        if not valid_fields:
            print("No valid fields found for duplicate check.")
            return False

        # Detect duplicates
        duplicates = df[df.duplicated(subset=valid_fields, keep=False)]
        
        if not duplicates.empty:
            print(f"Found {len(duplicates)} duplicate records.")
            # Save first 100 duplicates to HTML to avoid massive files
            report_df = duplicates.head(100)
            os.makedirs(os.path.dirname(output_html_path), exist_ok=True)
            report_df.to_html(output_html_path, index=False, classes='table table-danger table-striped')
            print(f"Duplicate records log saved to {output_html_path}")
            return True
        else:
            print("No duplicates detected.")
            # Save empty placeholder
            with open(output_html_path, 'w', encoding='utf-8') as f:
                f.write(f"<p>No duplicates detected for {year_label}.</p>")
            return False
    except Exception as e:
        print(f"Error detecting duplicates: {e}")
        return False
