# 09_prepare_ligands.py
import os
import re
import pandas as pd
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation, PDBQTWriterLegacy

INPUT_CSV = "data/top50_candidates.csv"
OUT_DIR   = "data/ligands_pdbqt"
os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(INPUT_CSV)
ok, failed = [], []

for _, row in df.iterrows():
    name   = str(row["drug_name"]).strip().replace(" ", "_").replace("/", "-")
    smiles = str(row["smiles"]).strip()

    # Strip CXSMILES annotations: anything after and including ' |'
    smiles = re.sub(r'\s*\|.*$', '', smiles).strip()

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        print(f"SKIP (bad SMILES): {name}")
        failed.append(name)
        continue

    mol = Chem.AddHs(mol)
    result = AllChem.EmbedMolecule(mol, AllChem.ETKDGv3())
    if result == -1:
        print(f"SKIP (embed failed): {name}")
        failed.append(name)
        continue

    AllChem.MMFFOptimizeMolecule(mol)

    preparator = MoleculePreparation()
    mol_setups = preparator.prepare(mol)
    if not mol_setups:
        print(f"SKIP (no mol_setup): {name}")
        failed.append(name)
        continue

    pdbqt_string, is_ok, error_msg = PDBQTWriterLegacy.write_string(mol_setups[0])
    if not is_ok:
        print(f"SKIP (pdbqt write failed): {name} — {error_msg}")
        failed.append(name)
        continue

    out_path = os.path.join(OUT_DIR, f"{name}.pdbqt")
    with open(out_path, "w") as f:
        f.write(pdbqt_string)
    print(f"OK: {name}")
    ok.append(name)

print(f"\nDone. {len(ok)} ligands prepared, {len(failed)} failed.")
if failed:
    print("Failed:", failed)