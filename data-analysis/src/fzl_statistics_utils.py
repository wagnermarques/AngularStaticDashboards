import pandas as pd
import plotly.graph_objects as go
import json
import os

def generate_bar_chart(df, x_col, y_col, title, output_html):
    """
    Generates a Plotly bar chart and saves it as HTML.
    """
    if df.empty:
        print("DataFrame is empty. Cannot generate chart.")
        return False

    print(f"Generating bar chart: {title}")
    try:
        fig = go.Figure(data=[
            go.Bar(name=y_col, x=df[x_col], y=df[y_col])
        ])
        
        fig.update_layout(
            title_text=title,
            xaxis_title=x_col,
            yaxis_title=y_col,
            template="plotly_white"
        )
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_html), exist_ok=True)
        
        fig.write_html(output_html, full_html=True, include_plotlyjs='cdn')
        print(f"Chart saved to {output_html}")
        return True
    except Exception as e:
        print(f"Error generating chart: {e}")
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
