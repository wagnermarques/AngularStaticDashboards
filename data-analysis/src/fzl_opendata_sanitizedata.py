
import pandas as pd

def fzl_opendata_detect_duplicate_records(df, subset_columns, update_original_df=True):
    """
    Detects duplicate records in a DataFrame based on a subset of columns.
    Returns a DataFrame with duplicate records.
    """
    if df.empty or not subset_columns:
        return pd.DataFrame()
    

    try:

        # detect and write duplicated records in a logfile
        duplicates = df[df.duplicated(subset=subset_columns, keep=False)]
        print(f"Found {len(duplicates)} duplicate records based on columns: {subset_columns}")
        
        # remove duplicated records if update_original_df is True
        if update_original_df:
            df.drop_duplicates(subset=subset_columns, keep='first', inplace=True)

        
        
        
        
        
        return duplicates
    except Exception as e:
        print(f"Error detecting duplicates: {e}")
        return pd.DataFrame()
