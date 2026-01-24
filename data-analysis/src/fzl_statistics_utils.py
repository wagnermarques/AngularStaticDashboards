import pandas as pd
import plotly.graph_objects as go
import plotly.utils
import json
import os

def generate_interactive_dashboard(data_views, title, output_html):
    """
    Generates an interactive HTML dashboard. 
    Supports simple bar charts and clustered bar charts.
    
    Args:
        data_views (dict): 
            Keys: View Name (e.g. "Por Estado")
            Values: {
                'df': DataFrame, 
                'x_col': str, 
                'y_col': str, 
                'x_label': str,
                'cluster_col': str (Optional - triggers clustered chart)
            }
    """
    if not data_views:
        print("No data views provided.")
        return False

    print(f"Generating interactive dashboard: {title}")
    
    try:
        js_data = {}
        
        for view_name, view_data in data_views.items():
            df = view_data['df']
            x_col = view_data['x_col']
            y_col = view_data['y_col']
            cluster_col = view_data.get('cluster_col') # New parameter
            
            traces = []
            table_html = ""

            if cluster_col and cluster_col in df.columns:
                # --- CLUSTERED LOGIC ---
                
                # Sort: usually alphabetical for X, chronological for Cluster
                df = df.sort_values(by=[x_col, cluster_col])
                
                # Get unique clusters (e.g., Years)
                clusters = sorted(df[cluster_col].unique())
                
                for cluster_val in clusters:
                    cluster_df = df[df[cluster_col] == cluster_val]
                    traces.append({
                        'x': cluster_df[x_col].tolist(),
                        'y': cluster_df[y_col].tolist(),
                        'name': str(cluster_val),
                        'type': 'bar'
                    })

                # Generate Pivot Table for cleaner display (X vs Cluster)
                pivot_df = df.pivot(index=x_col, columns=cluster_col, values=y_col).fillna(0)
                # Format numbers
                for c in pivot_df.columns:
                    pivot_df[c] = pivot_df[c].apply(lambda x: f"{int(x):,}".replace(",", "."))
                
                pivot_df.index.name = view_data.get('x_label', x_col)
                table_html = pivot_df.reset_index().to_html(classes='table table-striped', index=False, border=0)

            else:
                # --- SINGLE SERIES LOGIC ---
                
                # Sort descending by value for Pareto-like view
                if pd.api.types.is_numeric_dtype(df[y_col]):
                    df = df.sort_values(by=y_col, ascending=False)
                if x_col == 'NU_ANO_CENSO':
                    df = df.sort_values(by=x_col, ascending=True)

                traces.append({
                    'x': df[x_col].tolist(),
                    'y': df[y_col].tolist(),
                    'type': 'bar',
                    'marker': {'color': '#1976d2'},
                    'name': 'Total'
                })

                # Standard Table
                formatted_df = df.copy()
                if pd.api.types.is_numeric_dtype(formatted_df[y_col]):
                    formatted_df[y_col] = formatted_df[y_col].apply(lambda x: f"{int(x):,}".replace(",", "."))
                
                formatted_df = formatted_df.rename(columns={x_col: view_data.get('x_label', x_col), y_col: 'Quantidade'})
                table_html = formatted_df.to_html(classes='table table-striped', index=False, border=0)
            
            js_data[view_name] = {
                'traces': traces,
                'table': table_html,
                'x_label': view_data.get('x_label', x_col),
                'is_clustered': bool(cluster_col)
            }

        js_json = json.dumps(js_data)

        full_html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{
            font-family: 'Roboto', sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #fff;
        }}
        .controls {{
            text-align: center;
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        select {{
            padding: 8px 16px;
            font-size: 16px;
            border-radius: 4px;
            border: 1px solid #ccc;
        }}
        .chart-container {{
            margin-bottom: 30px;
            height: 500px;
        }}
        .table-container {{
            width: 100%;
            max-width: 1000px;
            margin: 0 auto;
            border: 1px solid #eee;
            border-radius: 8px;
            overflow-x: auto; /* Allow scroll for wide pivot tables */
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
            text-align: center;
            white-space: nowrap; /* Prevent wrapping in pivot tables */
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
    <div class="controls">
        <label for="viewSelector">Visualizar por: </label>
        <select id="viewSelector" onchange="updateView()">
            {''.join([f'<option value="{k}">{k}</option>' for k in data_views.keys()])}
        </select>
    </div>

    <div id="chartDiv" class="chart-container"></div>
    
    <div class="table-container">
        <h3>Tabela de Frequência</h3>
        <div id="tableDiv"></div>
    </div>

    <script>
        const dashboardData = {js_json};
        
        function updateView() {{
            const key = document.getElementById('viewSelector').value;
            const data = dashboardData[key];
            
            const layout = {{
                title: '{title}',
                xaxis: {{ type: 'category', title: data.x_label, automargin: true }},
                yaxis: {{ title: 'Quantidade' }},
                template: 'plotly_white',
                margin: {{ t: 40, b: 100, l: 60, r: 20 }},
                barmode: data.is_clustered ? 'group' : 'relative',
                autosize: true,
                legend: {{ orientation: 'h', y: 1.1 }}
            }};
            
            const config = {{ responsive: true, displayModeBar: false }};
            
            // Use newPlot to handle changing number of traces cleanly
            Plotly.newPlot('chartDiv', data.traces, layout, config);
            document.getElementById('tableDiv').innerHTML = data.table;
        }}

        // Initialize
        updateView();
        
        window.onresize = function() {{
            Plotly.Plots.resize('chartDiv');
        }};
    </script>
</body>
</html>"""

        os.makedirs(os.path.dirname(output_html), exist_ok=True)
        with open(output_html, 'w', encoding='utf-8') as f:
            f.write(full_html_content)
            
        print(f"Interactive dashboard saved to {output_html}")
        return True
    except Exception as e:
        print(f"Error generating dashboard: {e}")
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