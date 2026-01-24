import pandas as pd
import plotly.graph_objects as go
import json
import os

def generate_bar_chart(df, x_col, y_col, title, output_html):
    """
    Generates a Plotly bar chart and a frequency table, saving them as a single HTML file.
    """
    if df.empty:
        print("DataFrame is empty. Cannot generate chart.")
        return False

    print(f"Generating bar chart with table: {title}")
    try:
        # 1. Generate Plotly Chart HTML (fragment)
        fig = go.Figure(data=[
            go.Bar(name=y_col, x=df[x_col], y=df[y_col])
        ])
        
        fig.update_layout(
            title_text=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            template="plotly_white"
        )
        
        plot_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

        # 2. Generate Frequency Table HTML (fragment)
        # Sort by year just in case
        if x_col in df.columns:
            df_sorted = df.sort_values(by=x_col)
        else:
            df_sorted = df
            
        # Select only relevant columns for the table
        table_df = df_sorted[[x_col, y_col]].copy()
        
        # Format numbers if they are integers/floats
        if pd.api.types.is_numeric_dtype(table_df[y_col]):
             # Format with thousands separator if needed, or just integer
            try:
                table_df[y_col] = table_df[y_col].apply(lambda x: f"{int(x):,}".replace(",", "."))
            except:
                pass

        table_html = table_df.to_html(classes='table table-striped', index=False, border=0)

        # 3. Combine into a full HTML page
        full_html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #fff;
        }}
        .chart-container {{
            margin-bottom: 30px;
        }}
        .table-container {{
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            border: 1px solid #eee;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        h3 {{
            text-align: center;
            color: #333;
            margin-top: 0;
            padding-top: 20px;
        }}
        table.table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}
        table.table th, table.table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        table.table th {{
            background-color: #f8f9fa;
            font-weight: 600;
            color: #555;
        }}
        table.table tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        table.table tr:hover {{
            background-color: #f1f1f1;
        }}
    </style>
</head>
<body>
    <div class="chart-container">
        {plot_html}
    </div>
    
    <div class="table-container">
        <h3>Tabela de Frequência</h3>
        {table_html}
    </div>
</body>
</html>"""

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_html), exist_ok=True)
        
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(full_html_content)
            
        print(f"Chart and table saved to {output_html}")
        return True
    except Exception as e:
        print(f"Error generating chart/table: {e}")
        import traceback
        traceback.print_exc()
        return False

def export_to_json(data, output_json):
    """
    Exports data (list or dict) to a JSON file.
    """
    print(f"Exporting data to {output_json}...")
    try:
        os.makedirs(os.path.dirname(output_json), exist_ok=True)
        with open(output_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"JSON saved to {output_json}")
        return True
    except Exception as e:
        print(f"Error exporting JSON: {e}")
        return False