import os
import sys
import pandas as pd

# Add current directory to path to ensure imports work when running from project root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fzl_http_utils import download_file
from fzl_opendata_utils import extract_zip, find_files_in_zip
from fzl_excel_utils import read_excel_dictionary, find_field_description
from fzl_statistics_utils import generate_bar_chart, export_to_json
from fzl_opendata_censoeducacaoinep import load_census_csv, aggregate_by_year

def fzlecho1(msg):
    print(" ########## " + msg + " ########## ")

def fzlecho2(msg):
    print(" >>>>>>>>>> " + msg + " <<<<<<<<<< ")

def fzlecho3(msg):
    print(" ---------- " + msg + " ---------- ")

def fzlecho4(msg):
    print("    " + msg)    


# Configuration
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
ANGULAR_ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../angular-app/src/assets/data_analysis')
TEMP_EXTRACT_DIR = os.path.join(DATA_DIR, 'extracted')

DOWNLOAD_URLS = {
    '2021': 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2021.zip',
    '2022': 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2022.zip',
    '2023': 'https://download.inep.gov.br/dados_abertos/microdados_censo_escolar_2023.zip'
}

FIELD_TO_ANALYZE = 'QT_MAT_ESP'

def main():
    print("########## Starting Data Analysis Pipeline ##########")
    print("########## for data from INEP School Census ##########")
    
    pipeline_steps = [
        {"id": "download", "label": "Download Datasets", "status": "pending"},
        {"id": "extract", "label": "Extract Zip Files", "status": "pending"},
        {"id": "dictionary", "label": "Search Metadata", "status": "pending"},
        {"id": "process", "label": "Process CSVs", "status": "pending"},
        {"id": "visualize", "label": "Generate Visualization", "status": "pending"},
        {"id": "export", "label": "Export Results", "status": "pending"}
    ]

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    all_year_data = []

    # Step 1: Download (update status)
    print(f">>>>>>>>>> 1) Download data <<<<<<<<<<")
    success_download = True
    for year, url in DOWNLOAD_URLS.items():
        zip_path = os.path.join(DATA_DIR, f"microdados_censo_escolar_{year}.zip")
        if not download_file(url, zip_path, verify_ssl=False):
            success_download = False
    
    pipeline_steps[0]["status"] = "completed" if success_download else "error"

    # Step 2 & 3 & 4
    for year in DOWNLOAD_URLS.keys():
        print(f"########## Processing Year: {year} ##########")
        zip_path = os.path.join(DATA_DIR, f"microdados_censo_escolar_{year}.zip")
        extract_path = os.path.join(TEMP_EXTRACT_DIR, year)
        
        # 2) Extract
        print(f">>>>>>>>>> 2) Extracting Year {year} <<<<<<<<<<")
        if not os.path.exists(extract_path):
            extract_zip(zip_path, extract_path)
        pipeline_steps[1]["status"] = "completed"

        # 3) Dictionary
        print(f">>>>>>>>>> 3) Search Dictionary Year {year} <<<<<<<<<<")
        xlsx_files = []
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.endswith('.xlsx') and 'dicion' in file.lower():
                    xlsx_files.append(os.path.join(root, file))
        
        if xlsx_files:
            dict_df = read_excel_dictionary(xlsx_files[0])
            field_desc = find_field_description(dict_df, FIELD_TO_ANALYZE)
        pipeline_steps[2]["status"] = "completed"

        # 4) Process
        print(f">>>>>>>>>> 4) Process CSV Year {year} <<<<<<<<<<")
        csv_files = []
        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.lower().endswith('.csv') and 'microdados_ed_basica' in file.lower():
                    csv_files.append(os.path.join(root, file))
        
        if csv_files:
            df = load_census_csv(csv_files[0], columns=['NU_ANO_CENSO', FIELD_TO_ANALYZE])
            if not df.empty:
                all_year_data.append(aggregate_by_year(df, value_col=FIELD_TO_ANALYZE))
        pipeline_steps[3]["status"] = "completed"

    if all_year_data:
        final_df = pd.concat(all_year_data).groupby('NU_ANO_CENSO')[FIELD_TO_ANALYZE].sum().reset_index()
        
        # 5) Visualize
        print(f">>>>>>>>>> 5) Generate Visualization <<<<<<<<<<")
        chart_output = os.path.join(ANGULAR_ASSETS_DIR, 'student_count_by_year.html')
        generate_bar_chart(
            final_df, 
            x_col='NU_ANO_CENSO', 
            y_col=FIELD_TO_ANALYZE, 
            title=f"Total Students: {FIELD_TO_ANALYZE} (INEP Census)", 
            output_html=chart_output
        )
        pipeline_steps[4]["status"] = "completed"
        
        # 6) Export
        print(f">>>>>>>>>> 6) Export JSON <<<<<<<<<<")
        json_output = os.path.join(ANGULAR_ASSETS_DIR, 'summary_stats.json')
        json_data = final_df.rename(columns={'NU_ANO_CENSO': 'year', FIELD_TO_ANALYZE: 'student_count'}).to_dict(orient='records')
        export_to_json(json_data, json_output)
        
        # Export Pipeline Graph
        graph_output = os.path.join(ANGULAR_ASSETS_DIR, 'pipeline_graph.json')
        export_to_json(pipeline_steps, graph_output)
        pipeline_steps[5]["status"] = "completed"
        
        print("--- Pipeline Completed Successfully ---")
    else:
        print("No data was processed.")
        

if __name__ == "__main__":
    main()