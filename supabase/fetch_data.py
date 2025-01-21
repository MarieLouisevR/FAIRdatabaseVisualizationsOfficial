import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, jsonify, send_file
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import io

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Retrieve Supabase URL and Key
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(url, key)

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML page

@app.route('/tables', methods=['GET'])
def get_tables():
    try:
        response = supabase.rpc('get_tables').execute()
        if hasattr(response, 'error') and response.error:
            return jsonify({'error': response.error.message}), 500
        tables = [table['table_name'] for table in response.data]
        return jsonify(tables)  # Return JSON list of tables
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/shannon-index/<table_name>', methods=['GET'])
def shannon_index_route(table_name):
    try:
        # Fetch the OTU data from the specified table
        response = supabase.from_(table_name).select('*').execute()
        if hasattr(response, 'error') and response.error:
            return jsonify({'error': response.error.message}), 500

        # Convert the response data to a DataFrame
        data = pd.DataFrame(response.data)

        # Detect orientation (assume if more columns than rows, OTUs are in columns)
        otu_in_columns = data.shape[1] > data.shape[0]

        if otu_in_columns:
            # OTUs in columns (original case)
            data.set_index('id', inplace=True)
            samples_data = data.T
        else:
            # OTUs in rows
            data.set_index('otu_id', inplace=True)  # Assume OTU IDs are in 'otu_id' column
            samples_data = data

        # Function to calculate Shannon Index
        def shannon_index(counts):
            proportions = counts / counts.sum()
            return -np.sum(proportions * np.log(proportions + 1e-10))

        # Calculate Shannon Index for each sample
        shannon_indices = samples_data.apply(shannon_index, axis=1)

        # Create a box plot for the Shannon Index
        plt.figure(figsize=(12, 8))
        sns.set(style="whitegrid")
        box_plot = sns.boxplot(data=shannon_indices, 
                               color='skyblue', 
                               fliersize=8, 
                               linewidth=2, 
                               palette='Set2')
        
        # Adding enhancements to the plot
        plt.title('Alpha Diversity - Shannon Index', fontsize=16, weight='bold')
        plt.ylabel('Shannon Index', fontsize=14)
        plt.xticks([0], ['Samples'], fontsize=12)
        
        # Customizing the ticks for clarity
        plt.yticks(fontsize=12)
        plt.grid(True, linestyle='--', alpha=0.7)
        
        # Adding a shadow to the boxplot for a more professional look
        for box in box_plot.artists:
            box.set_facecolor('skyblue')
            box.set_edgecolor('darkblue')
            box.set_linewidth(2)
            box.set_alpha(0.7)

        # Save the plot to a BytesIO object
        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()

        # Send the image as a response
        return send_file(img, mimetype='image/png')
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
