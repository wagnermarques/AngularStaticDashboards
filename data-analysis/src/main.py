import os
import sys
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from fzl_http_utils import download_file
from fzl_opendata_utils import (
    extract_zip, 
    fzl_opendata_list_fields_in_dictionary_excel_file,
    fzl_opendata_detect_duplicate_records,
    fzl_opendata_get_field_description
)
from fzl_excel_utils import read_excel_dictionary, find_field_description
from fzl_statistics_utils import generate_interactive_dashboard, export_to_json
from fzl_opendata_censoeducacaoinep import load_census_csv, aggregate_by_year


# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
ANGULAR_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../angular-app/src/assets/data_analysis')
TEMP_EXTRACT_DIR = os.path.join(DATA_DIR, 'extracted')

DOWNLOAD_URLS = {
    '2021': 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2021.zip',
    '2022': 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2022.zip',
    '2023': 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2023.zip'
}

FIELD_TO_ANALYZE = 'QT_MAT_ESP' #Número de Matrículas da Educação Especial


def main():
    print("########## Starting Data Analysis Pipeline ##########")
    print("########## for data from INEP School Census ##########")
    
    pipeline_steps = [
        {"id": "download", "label": "Download Datasets", "status": "pending"},
        {"id": "extract", "label": "Extract Zip Files", "status": "pending"},
        {"id": "dictionary", "label": "Search Metadata", "status": "pending"},
        {"id": "sanitize", "label": "Sanitize Data", "status": "pending"},
        {"id": "process", "label": "Process CSVs", "status": "pending"},
        {"id": "visualize", "label": "Generate Visualization", "status": "pending"},
        {"id": "export", "label": "Export Results", "status": "pending"}
    ]

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    all_years_data = []
    all_states_data = []
    field_description_text = None

    # Step 1: Download
    print(f">>>>>>>>>> 1) Download data <<<<<<<<<<")
    success_download = True
    for year, url in DOWNLOAD_URLS.items():
        zip_path = os.path.join(DATA_DIR, f"microdados_censo_escolar_{year}.zip")
        if not download_file(url, zip_path, verify_ssl=False):
            success_download = False
    pipeline_steps[0]["status"] = "completed" if success_download else "error"

    for year in DOWNLOAD_URLS.keys():
        print(f"########## Processing Year: {year} ##########")
        zip_path = os.path.join(DATA_DIR, f"microdados_censo_escolar_{year}.zip")
        extract_path = os.path.join(TEMP_EXTRACT_DIR, year)
        
        # 2) Extract
        print(f">>>>>>>>>> 2) Extracting Year {year} <<<<<<<<<<")
        if not os.path.exists(extract_path):
            extract_zip(zip_path, extract_path)
        pipeline_steps[1]["status"] = "completed"

        # 3) Dictionary Metadata Listing
        print(f">>>>>>>>>> 3) Search Dictionary Year {year} <<<<<<<<<<")
        xlsx_files = []
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.endswith('.xlsx') and 'dicion' in file.lower():
                    xlsx_files.append(os.path.join(root, file))
        
        variable_names = []
        if xlsx_files:
            dict_html_path = os.path.join(ANGULAR_ASSETS_DIR, f'dictionary_{year}.html')
            variable_names = fzl_opendata_list_fields_in_dictionary_excel_file(xlsx_files[0], dict_html_path)
            
            # Attempt to fetch description for the analyzed field (if not already found)
            if not field_description_text:
                desc = fzl_opendata_get_field_description(xlsx_files[0], FIELD_TO_ANALYZE)
                if desc:
                    field_description_text = desc
                    print(f"Found description for {FIELD_TO_ANALYZE}: {field_description_text}")

        pipeline_steps[2]["status"] = "completed"

        # 4) Sanitize (Duplicate Detection)
        print(f">>>>>>>>>> 4) Sanitizing Year {year} <<<<<<<<<<")
        csv_files = []
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.lower().endswith('.csv') and 'microdados_ed_basica' in file.lower():
                    csv_files.append(os.path.join(root, file))
        
        if csv_files:
            # Clean variables from dictionary to match CSV headers
            clean_vars = [v.strip().upper() for v in variable_names]
            cols_to_use = clean_vars[:10] if clean_vars else []
            
            # Ensure Essential Columns
            required_cols = ['NU_ANO_CENSO', 'NO_UF', FIELD_TO_ANALYZE]
            for c in required_cols:
                if c not in cols_to_use: cols_to_use.append(c)
            
            # Use 'CO_ENTIDADE' for deduplication if possible
            if 'CO_ENTIDADE' in clean_vars and 'CO_ENTIDADE' not in cols_to_use:
                cols_to_use.append('CO_ENTIDADE')

            df = load_census_csv(csv_files[0], columns=cols_to_use)
            if not df.empty:
                dup_html_path = os.path.join(ANGULAR_ASSETS_DIR, f'duplicates_{year}.html')
                check_fields = ['CO_ENTIDADE'] if 'CO_ENTIDADE' in df.columns else cols_to_use[:3]
                fzl_opendata_detect_duplicate_records(df, check_fields, dup_html_path, year)
                
                # 5) Process (Aggregation)
                print(f">>>>>>>>>> 5) Process CSV Year {year} <<<<<<<<<<")
                
                # By Year
                agg_year = aggregate_by_year(df, value_col=FIELD_TO_ANALYZE)
                all_years_data.append(agg_year)
                
                # By State (NO_UF)
                if 'NO_UF' in df.columns:
                    # Convert to numeric first to ensure sum works
                    df[FIELD_TO_ANALYZE] = pd.to_numeric(df[FIELD_TO_ANALYZE], errors='coerce').fillna(0)
                    # Group by both UF and Year to allow clustering
                    agg_state = df.groupby(['NO_UF', 'NU_ANO_CENSO'])[FIELD_TO_ANALYZE].sum().reset_index()
                    all_states_data.append(agg_state)
        
        pipeline_steps[3]["status"] = "completed"
        pipeline_steps[4]["status"] = "completed"

    if all_years_data:
        # Final Aggregation
        final_df_year = pd.concat(all_years_data).groupby('NU_ANO_CENSO')[FIELD_TO_ANALYZE].sum().reset_index()
        
        final_df_state = pd.DataFrame()
        if all_states_data:
            # Aggregate again just in case, keeping Year for clustering
            final_df_state = pd.concat(all_states_data).groupby(['NO_UF', 'NU_ANO_CENSO'])[FIELD_TO_ANALYZE].sum().reset_index()
        
        # 6) Visualize
        print(f">>>>>>>>>> 6) Generate Visualization <<<<<<<<<<")
        chart_output = os.path.join(ANGULAR_ASSETS_DIR, 'student_count_by_year.html')
        
        chart_title = f"Total Students: {FIELD_TO_ANALYZE}"
        if field_description_text:
            chart_title += f" - {field_description_text}"
        chart_title += " (INEP Census)"
        
        # Define views for the interactive dashboard
        data_views = {
            'Por Ano': {
                'df': final_df_year,
                'x_col': 'NU_ANO_CENSO',
                'y_col': FIELD_TO_ANALYZE,
                'x_label': 'Ano do Censo'
            }
        }
        
        if not final_df_state.empty:
            data_views['Por Estado'] = {
                'df': final_df_state,
                'x_col': 'NO_UF',
                'y_col': FIELD_TO_ANALYZE,
                'x_label': 'Unidade da Federação',
                'cluster_col': 'NU_ANO_CENSO' # Trigger clustered chart
            }

        generate_interactive_dashboard(data_views, chart_title, chart_output)
        pipeline_steps[5]["status"] = "completed"
        
        # 7) Export
        print(f">>>>>>>>>> 7) Export JSON <<<<<<<<<<")
        json_output = os.path.join(ANGULAR_ASSETS_DIR, 'summary_stats.json')
        json_data = final_df_year.rename(columns={'NU_ANO_CENSO': 'year', FIELD_TO_ANALYZE: 'student_count'}).to_dict(orient='records')
        export_to_json(json_data, json_output)
        
        graph_output = os.path.join(ANGULAR_ASSETS_DIR, 'pipeline_graph.json')
        export_to_json(pipeline_steps, graph_output)
        pipeline_steps[6]["status"] = "completed"
        
        print("--- Pipeline Completed Successfully ---")
    else:
        print("No data was processed.")

if __name__ == "__main__":
    main()
