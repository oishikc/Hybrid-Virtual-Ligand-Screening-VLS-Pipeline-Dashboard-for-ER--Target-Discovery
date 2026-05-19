# 08_receptor_to_pdbqt.py
import os
import sys

input_pdb    = os.path.join("data", "1ERE_fixed.pdb")
cleaned_pdb  = os.path.join("data", "1ERE_clean.pdb")
output_pdbqt = os.path.join("data", "1ERE_receptor.pdbqt")

# --- Step 1: Clean PDB ---
print("## Step 1: Text-filtering PDB...")
cleaned_lines = []
with open(input_pdb) as f:
    for line in f:
        if line.startswith("ATOM  "):
            alt_loc = line[16]
            if alt_loc not in (" ", "A", "1"):
                continue
            line = line[:16] + " " + line[17:]
            if len(line) >= 80:
                line = line[:78] + "  " + line[80:]
            cleaned_lines.append(line)
        elif line.startswith(("TER", "END")):
            cleaned_lines.append(line)

if not any(l.startswith("END") for l in cleaned_lines):
    cleaned_lines.append("END\n")

with open(cleaned_pdb, "w") as f:
    f.writelines(cleaned_lines)

atom_count = sum(1 for l in cleaned_lines if l.startswith("ATOM"))
print(f"-> {cleaned_pdb} ({atom_count} ATOM records)")

# --- Step 2: Convert via Python API ---
print("\n## Step 2: Converting to PDBQT via meeko Python API...")

from meeko import Polymer, PDBQTWriterLegacy, ResidueChemTemplates, MoleculePreparation

with open(cleaned_pdb) as f:
    pdb_string = f.read()

print("Building chem_templates and mk_prep...")
chem_templates = ResidueChemTemplates.create_from_defaults()
mk_prep = MoleculePreparation()

print("Parsing polymer...")
try:
    polymer = Polymer.from_pdb_string(
        pdb_string,
        chem_templates,
        mk_prep,
        allow_bad_res=True   # skip problem residues instead of crashing
    )
except Exception as e:
    print(f"[ERROR] from_pdb_string failed: {e}")
    sys.exit(1)

print("Writing PDBQT...")
try:
    result = PDBQTWriterLegacy.write_string_from_polymer(polymer)
    output, failures = result if isinstance(result, tuple) else (result, [])
except Exception as e:
    print(f"[ERROR] write_string_from_polymer failed: {e}")
    sys.exit(1)

if failures:
    print(f"WARNING: {len(failures)} residues skipped:")
    for fail in failures[:10]:
        print(f"  {fail}")
    if len(failures) > 10:
        print(f"  ... and {len(failures) - 10} more")

if not output or not output.strip():
    print("[ERROR] PDBQT output is empty.")
    sys.exit(1)

with open(output_pdbqt, "w") as f:
    f.write(output)

out_atoms = sum(1 for l in output.splitlines() if l.startswith("ATOM"))
print(f"\n[SUCCESS] {output_pdbqt} — {out_atoms} ATOM records")
if out_atoms < 500:
    print("WARNING: Low atom count — receptor may be incomplete")

if os.path.exists(cleaned_pdb):
    os.remove(cleaned_pdb)