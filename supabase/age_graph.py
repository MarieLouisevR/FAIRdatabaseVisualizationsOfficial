from flask import Flask, request, render_template
from supabase import create_client, Client
import os
import pandas as pd
import matplotlib.pyplot as plt
import mpld3

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Retrieve Supabase URL and Key
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(url, key)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user input from the form
        age_column = request.form['age_column']  # Assuming user inputs column name
        
        # Fetch data from Supabase
        response = supabase.from_("microbiome-data").select("*").execute()
        
        if response.data is None:
            return "Error fetching data"

        data = response.data
        df = pd.DataFrame(data)

        # Generate the plot based on user input
        plt.figure(figsize=(12, 6))
        age_counts = df[age_column].value_counts().sort_index()
        plt.bar(age_counts.index, age_counts.values, color='skyblue')
        plt.xlabel('Age (Years)')
        plt.ylabel('Number of Samples')
        plt.title('Distribution of Ages in Microbiome Samples')
        plt.xticks(rotation=45)
        
        # Convert plot to HTML using mpld3
        html_str = mpld3.fig_to_html(plt.gcf())
        plt.close()  # Close the plot to free memory
        
        return render_template('index.html', plot=html_str)

    return render_template('index.html', plot=None)

if __name__ == '__main__':
    app.run(debug=True)
