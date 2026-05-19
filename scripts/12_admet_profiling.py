"""
Phase 4 — ADMET (Absorption, Distribution, Metabolism, Excretion, Toxicity)
profiling of the final ranked candidates using RDKit descriptors.

Properties computed
───────────────────
Lipinski Rule-of-Five
  MW          Molecular weight (< 500 Da)
  LogP        Wildman-Crippen LogP (< 5)
  HBD         H-bond donors (< 5)
  HBA         H-bond acceptors (< 10)
  lipinski_ok All four rules pass

Additional drug-likeness
  TPSA        Topological polar surface area (< 140 Å²  for oral; < 90 for CNS)
  RotBonds    Rotatable bonds (< 10 for oral bioavailability)
  RingCount   Number of rings
  AromaticRings  Number of aromatic rings
  Fsp3        Fraction sp3 carbons (> 0.25 correlates with better ADMET)
  QED         Quantitative Estimate of Drug-likeness (0–1, higher better)

Rough oral Cmax estimation (Veber / empirical)
  BioavailScore  0–1 rough oral bioavailability flag (Veber: TPSA ≤ 140, RotBonds ≤ 10)
  LogCmax_est    Rough log10(Cmax [nM]) based on dose 10 mg/kg oral, MW, F_oral estimate

Toxicity alerts (structural filters)
  PAINS_alert    Pan-assay interference (PAINS-A filter)
  Alarm_NMR      Reactive / problematic groups (REOS / Alarm-NMR surrogate)

Output
──────
data/admet_results.csv       – full ADMET table joined to final_ranked_candidates.csv
data/admet_summary.txt       – human-readable pass/fail summary
"""

import re
import sys
import warnings
import pandas as pd
import numpy as np
from pathlib import Path

# RDKit imports
try:
    from rdkit import Chem
    from rdkit.Chem import Descriptors, rdMolDescriptors, QED, FilterCatalog
    from rdkit.Chem.FilterCatalog import FilterCatalogParams
except ImportError:
    sys.exit("[ERROR] rdkit not found. Activate your conda environment: "
             "conda activate drug_repurpose")

warnings.filterwarnings("ignore")

# paths
DATA_DIR   = Path("data")
INPUT_CSV  = DATA_DIR / "final_ranked_candidates.csv"
OUT_CSV    = DATA_DIR / "admet_results.csv"
SUMMARY    = DATA_DIR / "admet_summary.txt"

# Lipinski thresholds
LIP_MW_MAX   = 500
LIP_LOGP_MAX = 5
LIP_HBD_MAX  = 5
LIP_HBA_MAX  = 10

# Veber oral bioavailability thresholds
VEBER_TPSA_MAX     = 140   # Å²
VEBER_ROTBONDS_MAX = 10


def strip_cxsmiles(smi: str) -> str:
    """Remove CXSMILES extension annotations."""
    return re.sub(r"\s*\|.*$", "", str(smi)).strip()


def build_pains_catalog():
    """Return PAINS-A FilterCatalog."""
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.PAINS_A)
    return FilterCatalog.FilterCatalog(params)


def build_alarm_catalog():
    """Return BRENK (Alarm-NMR surrogate) FilterCatalog."""
    params = FilterCatalogParams()
    params.AddCatalog(FilterCatalogParams.FilterCatalogs.BRENK)
    return FilterCatalog.FilterCatalog(params)


def profile_molecule(smiles: str, pains_cat, alarm_cat) -> dict:
    """Compute all ADMET descriptors for one SMILES string."""
    result = {
        "MW": np.nan, "LogP": np.nan, "HBD": np.nan, "HBA": np.nan,
        "TPSA": np.nan, "RotBonds": np.nan, "RingCount": np.nan,
        "AromaticRings": np.nan, "Fsp3": np.nan, "QED": np.nan,
        "lipinski_ok": False, "veber_ok": False,
        "BioavailScore": np.nan, "LogCmax_est": np.nan,
        "PAINS_alert": False, "Alarm_NMR": False,
        "mol_valid": False, "admet_note": "",
    }

    smi_clean = strip_cxsmiles(smiles)
    mol = Chem.MolFromSmiles(smi_clean)
    if mol is None:
        result["admet_note"] = "invalid SMILES"
        return result

    result["mol_valid"] = True

    # Basic physicochemical
    result["MW"]           = Descriptors.ExactMolWt(mol)
    result["LogP"]         = Descriptors.MolLogP(mol)
    result["HBD"]          = rdMolDescriptors.CalcNumHBD(mol)
    result["HBA"]          = rdMolDescriptors.CalcNumHBA(mol)
    result["TPSA"]         = rdMolDescriptors.CalcTPSA(mol)
    result["RotBonds"]     = rdMolDescriptors.CalcNumRotatableBonds(mol)
    result["RingCount"]    = rdMolDescriptors.CalcNumRings(mol)
    result["AromaticRings"]= rdMolDescriptors.CalcNumAromaticRings(mol)
    result["Fsp3"]         = rdMolDescriptors.CalcFractionCSP3(mol)

    # QED
    try:
        result["QED"] = QED.qed(mol)
    except Exception:
        result["QED"] = np.nan

    # Lipinski Ro5
    lip_pass = (
        result["MW"]   <= LIP_MW_MAX and
        result["LogP"] <= LIP_LOGP_MAX and
        result["HBD"]  <= LIP_HBD_MAX and
        result["HBA"]  <= LIP_HBA_MAX
    )
    result["lipinski_ok"] = lip_pass

    # Veber oral bioavailability
    veber_pass = (
        result["TPSA"]     <= VEBER_TPSA_MAX and
        result["RotBonds"] <= VEBER_ROTBONDS_MAX
    )
    result["veber_ok"] = veber_pass

    # BioavailScore: 1 if both Lipinski and Veber pass, 0.5 if one, 0 if none
    n_pass = int(lip_pass) + int(veber_pass)
    result["BioavailScore"] = n_pass / 2.0

    # Rough LogCmax estimate
    # Assumptions: dose = 10 mg/kg, BW = 70 kg, Vd ~ 0.6 L/kg (average oral drug)
    # F_oral estimated from Veber compliance (0.3 if fails, 0.7 if passes)
    dose_mg  = 10 * 70          # 700 mg total dose
    mw       = result["MW"] if result["MW"] > 0 else 500
    dose_mol = (dose_mg / mw) * 1e6  # nmol
    f_oral   = 0.70 if veber_pass else 0.30
    vd_l     = 0.6 * 70         # ~42 L
    cmax_nM  = (f_oral * dose_mol) / vd_l
    result["LogCmax_est"] = float(np.log10(cmax_nM)) if cmax_nM > 0 else np.nan

    # PAINS
    try:
        result["PAINS_alert"] = len(pains_cat.GetMatches(mol)) > 0
    except Exception:
        result["PAINS_alert"] = False

    # Alarm NMR (BRENK)
    try:
        result["Alarm_NMR"] = len(alarm_cat.GetMatches(mol)) > 0
    except Exception:
        result["Alarm_NMR"] = False

    return result


def main():
    print("=" * 60)
    print("  Phase 4 — ADMET Profiling")
    print("=" * 60)

    if not INPUT_CSV.exists():
        sys.exit(f"[ERROR] {INPUT_CSV} not found. Run 11_analyze_results.py first.")

    df = pd.read_csv(INPUT_CSV)
    print(f"[OK] Loaded final ranked candidates: {len(df)} compounds")

    if "smiles" not in df.columns:
        sys.exit("[ERROR] 'smiles' column not found in final_ranked_candidates.csv")

    # Build filter catalogs once
    pains_cat = build_pains_catalog()
    alarm_cat = build_alarm_catalog()
    print("[OK] PAINS-A and BRENK filter catalogs loaded")

    # Compute ADMET for each compound
    records = []
    for _, row in df.iterrows():
        desc = profile_molecule(str(row["smiles"]), pains_cat, alarm_cat)
        records.append(desc)

    admet_df = pd.DataFrame(records)

    # Merge with original
    result = pd.concat([df.reset_index(drop=True), admet_df], axis=1)

    # Drug-like overall flag
    result["drug_like"] = (
        result["lipinski_ok"] &
        result["veber_ok"] &
        (~result["PAINS_alert"]) &
        (~result["Alarm_NMR"])
    )

    # Sort by composite_rank (already sorted, but keep it tidy)
    if "composite_rank" in result.columns:
        result = result.sort_values("composite_rank")

    result.to_csv(OUT_CSV, index=False)
    print(f"\n[SAVED] ADMET results → {OUT_CSV}")

    
    print("\n" + "=" * 60)
    print("  ADMET SUMMARY — TOP 15 CANDIDATES")
    print("=" * 60)

    display_cols = [
        "drug_name", "vina_score", "binding_score",
        "MW", "LogP", "HBD", "HBA", "TPSA", "RotBonds",
        "QED", "lipinski_ok", "veber_ok", "PAINS_alert", "drug_like",
    ]
    display_cols = [c for c in display_cols if c in result.columns]

    with pd.option_context("display.max_rows", 20,
                           "display.float_format", "{:.2f}".format,
                           "display.max_colwidth", 26):
        print(result[display_cols].head(15).to_string(index=False))

    # Stats
    n_valid      = result["mol_valid"].sum()
    n_lipinski   = result["lipinski_ok"].sum()
    n_veber      = result["veber_ok"].sum()
    n_pains      = result["PAINS_alert"].sum()
    n_alarm      = result["Alarm_NMR"].sum()
    n_drug_like  = result["drug_like"].sum()
    n_strong_hit = result.get("strong_hit", pd.Series([False]*len(result))).sum()
    n_combined   = (result["drug_like"] & result.get("strong_hit", False)).sum() \
                   if "strong_hit" in result.columns else 0

    print(f"\n  Valid structures    : {n_valid}/{len(result)}")
    print(f"  Lipinski Ro5 pass  : {n_lipinski}")
    print(f"  Veber oral pass    : {n_veber}")
    print(f"  PAINS alerts       : {n_pains}")
    print(f"  Alarm-NMR alerts   : {n_alarm}")
    print(f"  Drug-like overall  : {n_drug_like}")
    if "strong_hit" in result.columns:
        print(f"  Strong docking hit : {n_strong_hit}")
        print(f"  Strong hit + Drug-like (prime candidates): {n_combined}")

    # Prime candidates
    if "strong_hit" in result.columns:
        prime = result[result["drug_like"] & result["strong_hit"]]
    else:
        prime = result[result["drug_like"]].head(5)

    print(f"\n  ★  PRIME REPURPOSING CANDIDATES  ★")
    if len(prime) == 0:
        print("  None meeting all criteria — consider relaxing thresholds.")
        # Fallback: drug-like top 5
        prime = result[result["drug_like"]].head(5)
        print("  Showing top-5 drug-like hits instead:")

    prime_cols = ["drug_name", "composite_rank", "vina_score",
                  "binding_score", "QED", "LogCmax_est", "drug_like"]
    prime_cols = [c for c in prime_cols if c in prime.columns]
    with pd.option_context("display.float_format", "{:.3f}".format,
                           "display.max_colwidth", 28):
        print(prime[prime_cols].to_string(index=False))

    #summary
    lines = [
        "Phase 4 — ADMET Profiling Summary",
        "=" * 52,
        f"Total compounds profiled     : {len(result)}",
        f"Valid RDKit structures       : {n_valid}",
        f"Lipinski Ro5 pass           : {n_lipinski}",
        f"Veber oral bioavail pass    : {n_veber}",
        f"PAINS-A alerts              : {n_pains}",
        f"Alarm-NMR (BRENK) alerts   : {n_alarm}",
        f"Fully drug-like             : {n_drug_like}",
        "",
        "Prime candidates (drug-like AND strong docking hit):",
        prime[prime_cols].to_string(index=False),
        "",
        "Descriptor thresholds used:",
        f"  Lipinski: MW<={LIP_MW_MAX}, LogP<={LIP_LOGP_MAX}, HBD<={LIP_HBD_MAX}, HBA<={LIP_HBA_MAX}",
        f"  Veber:    TPSA<={VEBER_TPSA_MAX} Å², RotBonds<={VEBER_ROTBONDS_MAX}",
        "  Tox:      PAINS-A negative, BRENK/Alarm-NMR negative",
        "",
        "Note: Cmax is a rough empirical estimate only.",
        "  Use PKCSM / pkSmart / SwissADME for clinical-grade prediction.",
        "",
        "Next: run 13_dashboard.py to launch Streamlit visualisation.",
    ]
    SUMMARY.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[SAVED] ADMET summary → {SUMMARY}")

if __name__ == "__main__":
    main()
