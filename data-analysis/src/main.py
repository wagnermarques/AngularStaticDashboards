import os
import sys
import pandas as pd

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


from fzl_http_utils import download_file
from fzl_opendata_utils import (
    extract_zip, 
    fzl_opendata_list_fields_in_dictionary_excel_file,
    fzl_opendata_detect_duplicate_records
)
from fzl_excel_utils import read_excel_dictionary, find_field_description
from fzl_statistics_utils import generate_bar_chart, export_to_json
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
        pipeline_steps[2]["status"] = "completed"

        # 4) Sanitize (Duplicate Detection)
        print(f">>>>>>>>>> 4) Sanitizing Year {year} <<<<<<<<<<")
        csv_files = []
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.lower().endswith('.csv') and 'microdados_ed_basica' in file.lower():
                    csv_files.append(os.path.join(root, file))
        
        if csv_files:
            # We load the full row to check duplicates based on dictionary fields
            # Clean variables from dictionary to match CSV headers
            clean_vars = [v.strip().upper() for v in variable_names]
            
            # For efficiency in this demo, we'll use a subset of the first 10 variables
            # Todo: In production, use this vars wich can be indicate possible same person record
            # DS_ENDERECO, DS_BAIRRO, NU_CEP, NU_TELEFONE, DS_EMAIL, CO_ENTIDADE(Código da Escola), CO_MUNICIPIO, CO_UF, TP_DEPENDENCIA_ADM, TP_LOCALIZACAO, DDD_TELEFONE, NU_DDD_CELULAR, NU_CELULAR
            cols_to_use = clean_vars[:10] if clean_vars else []
            
            # Ensure NU_ANO_CENSO and FIELD_TO_ANALYZE are included
            if 'NU_ANO_CENSO' not in cols_to_use: cols_to_use.append('NU_ANO_CENSO')
            if FIELD_TO_ANALYZE not in cols_to_use: cols_to_use.append(FIELD_TO_ANALYZE)
            
            df = load_census_csv(csv_files[0], columns=cols_to_use)
            if not df.empty:
                dup_html_path = os.path.join(ANGULAR_ASSETS_DIR, f'duplicates_{year}.html')
                # Use CO_ENTIDADE for meaningful duplicate detection in School Census
                check_fields = ['CO_ENTIDADE'] if 'CO_ENTIDADE' in df.columns else cols_to_use[:3]
                fzl_opendata_detect_duplicate_records(df, check_fields, dup_html_path, year)
                
                # 5) Process (Aggregation)
                print(f">>>>>>>>>> 5) Process CSV Year {year} <<<<<<<<<<")
                aggregated = aggregate_by_year(df, value_col=FIELD_TO_ANALYZE)
                all_years_data.append(aggregated)
        
        pipeline_steps[3]["status"] = "completed"
        pipeline_steps[4]["status"] = "completed"

    if all_years_data:
        final_df = pd.concat(all_years_data).groupby('NU_ANO_CENSO')[FIELD_TO_ANALYZE].sum().reset_index()
        
        # 6) Visualize
        print(f">>>>>>>>>> 6) Generate Visualization <<<<<<<<<<")
        chart_output = os.path.join(ANGULAR_ASSETS_DIR, 'student_count_by_year.html')
        generate_bar_chart(
            final_df, 
            x_col='NU_ANO_CENSO', 
            y_col=FIELD_TO_ANALYZE, 
            title=f"Total Students: {FIELD_TO_ANALYZE} (INEP Census)", 
            output_html=chart_output
        )
        pipeline_steps[5]["status"] = "completed"
        
        # 7) Export
        print(f">>>>>>>>>> 7) Export JSON <<<<<<<<<<")
        json_output = os.path.join(ANGULAR_ASSETS_DIR, 'summary_stats.json')
        json_data = final_df.rename(columns={'NU_ANO_CENSO': 'year', FIELD_TO_ANALYZE: 'student_count'}).to_dict(orient='records')
        export_to_json(json_data, json_output)
        
        graph_output = os.path.join(ANGULAR_ASSETS_DIR, 'pipeline_graph.json')
        export_to_json(pipeline_steps, graph_output)
        pipeline_steps[6]["status"] = "completed"
        
        print("--- Pipeline Completed Successfully ---")
    else:
        print("No data was processed.")

if __name__ == "__main__":
    main()
