import pandas as pd
import os

def read_excel_dictionary(file_path, sheet_name=0):
    """
    Reads an Excel dictionary and returns a DataFrame.
    """
    if not os.path.exists(file_path):
        print(f"Excel file not found: {file_path}")
        return None
        
    try:
        # We might need to specify the header row or skip some rows depending on the file
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df
    except Exception as e:
        print(f"Error reading Excel dictionary: {e}")
        return None

def find_field_description(df, field_name, name_col='Nome da Variável', desc_col='Descrição'):
    """
    Finds the description of a specific field in the dictionary DataFrame.
    Note: column names might vary by year/source.
    """
    if df is None or field_name is None:
        return None
        
    # Try to find columns if they don't match exactly
    cols = df.columns.tolist()
    actual_name_col = next((c for c in cols if name_col.lower() in str(c).lower()), None)
    actual_desc_col = next((c for c in cols if desc_col.lower() in str(c).lower()), None)
    
    if not actual_name_col:
        # Fallback to first column
        actual_name_col = cols[0]
    if not actual_desc_col:
        # Fallback to second or third column
        actual_desc_col = cols[min(2, len(cols)-1)]

    result = df[df[actual_name_col].astype(str).str.contains(field_name, case=False, na=False)]
    if not result.empty:
        return result[actual_desc_col].iloc[0]
    return f"No description found for {field_name}"
