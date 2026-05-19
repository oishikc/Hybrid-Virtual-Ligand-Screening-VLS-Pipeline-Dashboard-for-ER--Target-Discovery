import pandas as pd
import re

# Parse the pretty-print table
rows = []
with open("./save_folder/results_aggregation/repurposing.txt", "r") as f:
    for line in f:
        # Match data rows: | rank | name | target | score |
        match = re.match(r'\|\s*(\d+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*([0-9.]+)\s*\|', line)
        if match:
            rows.append({
                'rank':          int(match.group(1)),
                'drug_name':     match.group(2).strip(),
                'target':        match.group(3).strip(),
                'binding_score': float(match.group(4))
            })

results_df = pd.DataFrame(rows)
print(f"Total compounds parsed: {len(results_df)}")
print(results_df.head(5))

# Extract top 50
top50 = results_df.head(50).copy()

# Get SMILES for top 50 from clean library
library = pd.read_csv("data/clean_ligand_library.csv")

# Merge on drug name
top50 = top50.merge(
    library[['pert_iname', 'smiles']],
    left_on='drug_name',
    right_on='pert_iname',
    how='left'
)

print(f"\nTop 50 with SMILES matched: {top50['smiles'].notna().sum()}")
print(top50[['rank', 'drug_name', 'binding_score', 'smiles']].head(10))

# Save
top50.to_csv("data/top50_candidates.csv", index=False)
results_df.to_csv("data/deeppurpose_results.csv", index=False)
print("\nSaved → data/top50_candidates.csv")