import pandas as pd
import numpy as np

# Sample OTU data
otus = [f"OTU_{i}" for i in range(1, 21)]
samples = [f"Sample_{i}" for i in range(1, 11)]
data = np.random.randint(0, 100, size=(20, 10))

# Create DataFrame
otu_table = pd.DataFrame(data, index=otus, columns=samples)
print(otu_table)


otu_table.to_csv('otu_table.csv')
