import pandas as pd

drugs = pd.read_csv("data/repurposing_drugs.txt", sep="\t", skiprows=9, low_memory=False)
samples = pd.read_csv("data/repurposing_samples.txt", sep="\t", skiprows=9, low_memory=False)

print("=== DRUGS FILE ===")
print("Shape:", drugs.shape)
print("Columns:", drugs.columns.tolist())
print(drugs.head(3))

print("\n=== SAMPLES FILE ===")
print("Shape:", samples.shape)
print("Columns:", samples.columns.tolist())
print(samples.head(3))
