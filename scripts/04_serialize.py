import pandas as pd
import json

df = pd.read_csv("data/clean_ligand_library.csv")

smiles_list = df['smiles'].tolist()
name_list   = df['pert_iname'].tolist()

output = {'names': name_list, 'smiles': smiles_list}

with open("data/smiles_list.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"Phase 1 complete.")
print(f"{len(smiles_list)} compounds serialized → data/smiles_list.json")
