# 10_docking.py
# Runs AutoDock Vina on all prepared ligands against 1ERE receptor

import os
import subprocess
import glob
import csv

VINA_BIN    = r".\vina.exe"
RECEPTOR    = "data/1ERE_receptor.pdbqt"
LIGAND_DIR  = "data/ligands_pdbqt"
OUT_DIR     = "data/docking_outputs"
RESULTS_CSV = "data/docking_scores.csv"

# ER-alpha binding site (from 1ERE crystal structure)
CENTER_X, CENTER_Y, CENTER_Z = 31.11, 45.32, 89.25
SIZE_X,   SIZE_Y,   SIZE_Z   = 25,    25,    25

os.makedirs(OUT_DIR, exist_ok=True)

ligand_files = sorted(glob.glob(os.path.join(LIGAND_DIR, "*.pdbqt")))
print(f"Found {len(ligand_files)} ligands to dock.\n")

results = []

for lig_path in ligand_files:
    name = os.path.splitext(os.path.basename(lig_path))[0]
    out_path = os.path.join(OUT_DIR, f"{name}_out.pdbqt")
    log_path = os.path.join(OUT_DIR, f"{name}_log.txt")

    cmd = [
        VINA_BIN,
        "--receptor", RECEPTOR,
        "--ligand",   lig_path,
        "--out",      out_path,
        "--center_x", str(CENTER_X),
        "--center_y", str(CENTER_Y),
        "--center_z", str(CENTER_Z),
        "--size_x",   str(SIZE_X),
        "--size_y",   str(SIZE_Y),
        "--size_z",   str(SIZE_Z),
        "--exhaustiveness", "8",
        "--num_modes",      "9",
    ]

    print(f"Docking {name}...")
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=300
        )
        log = proc.stdout + proc.stderr

        with open(log_path, "w") as f:
            f.write(log)

        # Parse best score (first mode, kcal/mol)
        best_score = None
        for line in log.splitlines():
            line = line.strip()
            if line.startswith("1 "):
                parts = line.split()
                try:
                    best_score = float(parts[1])
                except (IndexError, ValueError):
                    pass
                break

        if best_score is not None:
            print(f"  → Best score: {best_score:.2f} kcal/mol")
            results.append({"name": name, "vina_score": best_score})
        else:
            print(f"  → Could not parse score (check {log_path})")
            results.append({"name": name, "vina_score": None})

    except subprocess.TimeoutExpired:
        print(f"  → TIMEOUT for {name}")
        results.append({"name": name, "vina_score": None})
    except Exception as e:
        print(f"  → ERROR: {e}")
        results.append({"name": name, "vina_score": None})

# Write raw docking scores
with open(RESULTS_CSV, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["name", "vina_score"])
    writer.writeheader()
    writer.writerows(results)

print(f"\nDocking complete. Scores saved to {RESULTS_CSV}")
