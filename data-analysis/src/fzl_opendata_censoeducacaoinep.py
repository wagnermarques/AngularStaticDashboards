import pandas as pd
import io
import zipfile
import os

def load_census_csv(file_handle_or_path, delimiter=';', encoding='latin1', columns=None):
    """
    Loads a census CSV file into a pandas DataFrame.
    """
    try:
        # If it's a file handle (from zip), we need to handle it carefully
        # pandas can read from file-like objects
        df = pd.read_csv(file_handle_or_path, delimiter=delimiter, encoding=encoding, usecols=columns, low_memory=False)
        return df
    except Exception as e:
        print(f"Error loading census CSV: {e}")
        return pd.DataFrame()

def aggregate_by_year(df, year_col='NU_ANO_CENSO', value_col='QT_MAT_ESP'):
    """
    Aggregates data by year, summing the values in value_col.
    """
    if df.empty or year_col not in df.columns or value_col not in df.columns:
        return pd.DataFrame()
        
    try:
        # Convert value_col to numeric just in case
        df[value_col] = pd.to_numeric(df[value_col], errors='coerce').fillna(0)
        grouped = df.groupby(year_col)[value_col].sum().reset_index()
        return grouped
    except Exception as e:
        print(f"Error aggregating data: {e}")
        return pd.DataFrame()

def find_dictionary_in_zip(zip_path):
    """
    Finds the path to the Excel dictionary inside the census zip.
    """
    from .fzl_opendata_utils import find_files_in_zip
    xlsx_files = find_files_in_zip(zip_path, '.xlsx')
    # Usually the dictionary has 'dicionario' in the name
    dict_files = [f for f in xlsx_files if 'dicionario' in f.lower()]
    return dict_files[0] if dict_files else None
