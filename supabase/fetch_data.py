import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from flask import Flask, render_template, jsonify, send_file, request
from supabase import create_client, Client
import os
from dotenv import load_dotenv
import io
from flask_cors import CORS

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Retrieve Supabase URL and Key
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(url, key)

debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

@app.route('/')
def index():
    return render_template('index2.html')  # Serve the HTML page

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

@app.route('/visualize/<table_name>', methods=['GET'])
def visualize_route(table_name):
    try:
        # Validate table name
        if not table_name or not isinstance(table_name, str):
            return jsonify({'error': 'Invalid table name'}), 400

        # Get the plot type from query parameters (default to 'boxplot')
        plot_type = request.args.get('plot_type', 'boxplot').lower()

        # Fetch the OTU data from the specified table
        response = supabase.from_(table_name).select('*').execute()
        if hasattr(response, 'error') and response.error:
            return jsonify({'error': response.error.message}), 500

        # Check if data is empty
        if not response.data:
            return jsonify({'error': 'No data found in the specified table'}), 404

        # Convert the response data to a DataFrame
        data = pd.DataFrame(response.data)

        # Assume the first column is the OTU column
        otu_column = data.columns[0]
        data.set_index(otu_column, inplace=True)

        # Detect orientation
        if data.shape[1] > data.shape[0]:
            samples_data = data.T
        else:
            samples_data = data

        # Plot generation logic
        if plot_type == 'scatter':
            # Calculate Shannon Index for each sample
            def shannon_index(counts):
                pseudocounts = counts + 1
                proportions = pseudocounts / pseudocounts.sum()
                return -np.sum(proportions * np.log(proportions))

            # Calculate Shannon Index for each sample (i.e., each column)
            shannon_indices = samples_data.apply(shannon_index, axis=0)

            # Assign a unique color to each sample based on sample names
            unique_colors = sns.color_palette("Set1", len(shannon_indices))

            # Create a scatter plot
            plt.figure(figsize=(12, 8))  # Increase figure size
            sns.set(style="whitegrid")

            # Plot each sample with a different color
            for i, (sample, value) in enumerate(shannon_indices.items()):
                plt.scatter(sample, value, color=unique_colors[i], s=100, alpha=0.7, label=sample)

            plt.title('Shannon Index for Each Sample', fontsize=16, weight='bold')
            plt.ylabel('Shannon Index', fontsize=14)

            # Remove x-axis labels and ticks
            plt.xticks([])  # No ticks on x-axis
            plt.xlabel('')  # Remove x-axis label

            # Add a legend for each sample and adjust its position to prevent cutoff
            plt.legend(title="Samples", bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=12)

            # Use tight_layout to ensure that everything fits properly
            plt.tight_layout()

            # Save the plot to a BytesIO object (or any other method you are using to send it)
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plt.close()

            # Send the image as a response (for Flask or similar frameworks)
            return send_file(img, mimetype='image/png')

        elif plot_type == 'boxplot':
            # Shannon Index Calculation for Boxplot
            def shannon_index(counts):
                pseudocounts = counts + 1
                proportions = pseudocounts / pseudocounts.sum()
                return -np.sum(proportions * np.log(proportions))

            # Calculate Shannon Index for each sample
            shannon_indices = samples_data.apply(shannon_index, axis=1)

            # Create a box plot
            plt.figure(figsize=(12, 8))
            sns.set(style="whitegrid")
            sns.boxplot(data=shannon_indices, 
                        color='skyblue', 
                        fliersize=8, 
                        linewidth=2, 
                        palette='Set2')
            plt.title('Alpha Diversity - Shannon Index', fontsize=16, weight='bold')
            plt.ylabel('Shannon Index', fontsize=14)
            plt.xticks([0], ['Samples'], fontsize=12)

            # Save the plot to a BytesIO object
            img = io.BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plt.close()

            # Send the image as a response
            return send_file(img, mimetype='image/png')
        
        else:
            return jsonify({'error': f'Invalid plot type: {plot_type}. Use "boxplot" or "scatter".'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
