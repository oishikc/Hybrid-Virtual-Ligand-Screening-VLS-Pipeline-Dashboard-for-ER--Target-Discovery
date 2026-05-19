# 07_prepare_receptor.py
from pdbfixer import PDBFixer
from openmm.app import PDBFile

print("Preparing 1ERE.pdb...")

fixer = PDBFixer(filename='data/1ERE.pdb')
fixer.removeHeterogens(keepWater=False)

# Skip findMissingAtoms/addMissingAtoms/addMissingHydrogens entirely
# 1ERE is a clean crystal structure; PDBFixer's additions cause RDKit valence errors

output_path = 'data/1ERE_fixed.pdb'
with open(output_path, 'w') as f:
    PDBFile.writeFile(fixer.topology, fixer.positions, f)

# Strip formal charges written by OpenMM
lines = open(output_path).readlines()
clean = []
for line in lines:
    if line.startswith("ATOM"):
        line = line.rstrip("\n").ljust(80)
        line = line[:78] + "  \n"
    clean.append(line)

with open(output_path, "w") as f:
    f.writelines(clean)

atom_count = sum(1 for l in clean if l.startswith("ATOM"))
print(f"Saved -> {output_path} ({atom_count} ATOM records)")