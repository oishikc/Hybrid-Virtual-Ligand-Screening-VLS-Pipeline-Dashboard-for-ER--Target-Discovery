import pandas as pd
from rdkit import Chem
from rdkit.Chem import Descriptors, rdMolDescriptors

# Load both files
drugs = pd.read_csv("data/repurposing_drugs.txt", sep="\t", skiprows=9, low_memory=False)
samples = pd.read_csv("data/repurposing_samples.txt", sep="\t", skiprows=9, low_memory=False)

# Normalize names before merging
drugs['pert_iname']   = drugs['pert_iname'].str.strip().str.lower()
samples['pert_iname'] = samples['pert_iname'].str.strip().str.lower()

# Merge
merged = pd.merge(samples, drugs, on="pert_iname", how="inner")
merged['pert_iname'] = merged['pert_iname'].fillna(merged['broad_id'])
print(f"Merged shape: {merged.shape}")
print(f"NaN clinical_phase: {merged['clinical_phase'].isna().sum()}")

# Filter to FDA-approved only
fda = merged[merged['clinical_phase'] == 'Launched'].copy()
print(f"FDA-approved (Launched): {len(fda)}")

# Drop duplicate SMILES
fda = fda.drop_duplicates(subset='smiles').copy()
print(f"After deduplication: {len(fda)}")

# Validate SMILES
def is_valid(smiles):
    if not isinstance(smiles, str):
        return False
    return Chem.MolFromSmiles(smiles) is not None

fda['valid'] = fda['smiles'].apply(is_valid)
clean = fda[fda['valid']].copy()
print(f"Valid SMILES: {len(clean)}")

# Drop empty rows
clean = clean.dropna(subset=['smiles', 'pert_iname']).copy()
print(f"After dropping empty rows: {len(clean)}")

# Compute molecular properties
def get_props(smiles):
    try:
        mol = Chem.MolFromSmiles(smiles)
        if mol is None:
            return None
        return {
            'MW':       Descriptors.MolWt(mol),
            'LogP':     Descriptors.MolLogP(mol),
            'HBD':      rdMolDescriptors.CalcNumHBD(mol),
            'HBA':      rdMolDescriptors.CalcNumHBA(mol),
            'TPSA':     Descriptors.TPSA(mol),
            'RotBonds': rdMolDescriptors.CalcNumRotatableBonds(mol)
        }
    except:
        return None

props = clean['smiles'].apply(get_props)
failed = props.isna().sum()
print(f"Property calculation failed for {failed} compounds")
props = props.dropna()
clean = clean.loc[props.index].copy()
props_df = props.apply(pd.Series)
clean = pd.concat([clean.reset_index(drop=True), props_df.reset_index(drop=True)], axis=1)

# Lipinski Ro5
ro5 = (
    (clean['MW']   <= 500) &
    (clean['LogP'] <= 5)   &
    (clean['HBD']  <= 5)   &
    (clean['HBA']  <= 10)
)
druglike = clean[ro5].copy()
print(f"After Lipinski filter: {len(druglike)} compounds")

# Save
druglike.to_csv("data/clean_ligand_library.csv", index=False)
print("Saved → data/clean_ligand_library.csv")