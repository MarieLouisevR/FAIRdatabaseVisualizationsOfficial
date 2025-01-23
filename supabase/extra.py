import pandas as pd
import numpy as np
import os

# Configurable parameters for dataset size
num_otus = 1000  # Number of OTUs
num_samples = 100  # Number of Samples

# Generate OTU and Sample names
otus = [f"OTU_{i}" for i in range(1, num_otus + 1)]
samples = [f"Sample_{i}" for i in range(1, num_samples + 1)]

# Generate random data
data = np.random.randint(1, 1000, size=(num_otus, num_samples))  # Larger range for counts

# Create DataFrame
otu_table = pd.DataFrame(data, index=otus, columns=samples)

# Print a preview of the dataset
print(otu_table.head())

# Define the directory and filename
output_dir = "mock_datasets"
output_file = os.path.join(output_dir, "otu_table_large.csv")

# Create the directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Save to CSV
otu_table.to_csv(output_file)

print(f"Dataset saved to {output_file}")
