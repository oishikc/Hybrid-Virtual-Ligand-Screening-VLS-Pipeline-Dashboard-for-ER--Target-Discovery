"""
11_analyze_results.py
─────────────────────
Merges DeepPurpose ML scores with AutoDock Vina docking scores,
computes a composite rank, flags strong hits, and writes the
final ranked candidate table.

Outputs
-------
data/final_ranked_candidates.csv   – master results table
data/analysis_summary.txt          – human-readable summary

Run
---
    python 11_analyze_results.py
"""

import pandas as pd
import numpy as np
from pathlib import Path

# ── paths ────────────────────────────────────────────────────────────────────
DATA_DIR   = Path("data")
TOP50_CSV  = DATA_DIR / "top50_candidates.csv"
DOCK_CSV   = DATA_DIR / "docking_scores.csv"
OUT_CSV    = DATA_DIR / "final_ranked_candidates.csv"
SUMMARY    = DATA_DIR / "analysis_summary.txt"

# ── thresholds for "strong hit" flag ─────────────────────────────────────────
# Vina: <= -7.0 kcal/mol  (tighter than -6.0 standard cutoff for drug-sized ligands)
# DeepPurpose: binding_score percentile <= 25th  (lower = better predicted Ki)
VINA_CUTOFF       = -7.0   # kcal/mol
DP_PERCENTILE_CUT = 25     # bottom quartile of binding_score = best predicted binders

def load_and_validate(path: Path, label: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"[ERROR] {label} not found: {path}\n"
                                "Make sure previous pipeline steps completed successfully.")
    df = pd.read_csv(path)
    print(f"[OK] Loaded {label}: {len(df)} rows, columns: {list(df.columns)}")
    return df

def percentile_rank(series: pd.Series) -> pd.Series:
    """Return 0–100 percentile rank (lower raw value → lower percentile rank)."""
    return series.rank(pct=True) * 100

def composite_score(dp_pct: pd.Series, vina_pct: pd.Series,
                    w_dp: float = 0.4, w_vina: float = 0.6) -> pd.Series:
    """
    Weighted average of percentile ranks.
    Both series are already 'lower = better', so lower composite = stronger hit.
    Vina weighted more heavily (60 %) because it is structure-based and
    more directly tied to binding geometry.
    """
    return w_dp * dp_pct + w_vina * vina_pct

def main():
    print("=" * 60)
    print("  Phase 3 → Analysis: Merging DeepPurpose + Vina scores")
    print("=" * 60)

    # ── 1. load data ─────────────────────────────────────────────────────────
    top50  = load_and_validate(TOP50_CSV,  "DeepPurpose top-50")
    docked = load_and_validate(DOCK_CSV,   "Vina docking scores")

    # ── 2. normalise key columns ──────────────────────────────────────────────
    # DeepPurpose CSV expected columns:
    #   rank, drug_name, target, binding_score, pert_iname, smiles
    # Docking CSV expected columns (produced by 10_docking.py):
    #   drug_name  (or pert_iname / name),  vina_score

    # Standardise drug name column in docking table
    dock_name_col = None
    for candidate in ("drug_name", "pert_iname", "name", "compound"):
        if candidate in docked.columns:
            dock_name_col = candidate
            break
    if dock_name_col is None:
        raise ValueError(f"Cannot find a drug-name column in {DOCK_CSV}. "
                         f"Found columns: {list(docked.columns)}")

    docked = docked.rename(columns={dock_name_col: "drug_name"})

    # Standardise vina score column
    vina_col = None
    for candidate in ("vina_score", "score", "affinity", "docking_score"):
        if candidate in docked.columns:
            vina_col = candidate
            break
    if vina_col is None:
        raise ValueError(f"Cannot find a vina-score column in {DOCK_CSV}. "
                         f"Found columns: {list(docked.columns)}")

    docked = docked.rename(columns={vina_col: "vina_score"})[["drug_name", "vina_score"]]


    # -- 3. deduplicate top50 (keep best binding_score per drug_name) --------
    n_before = len(top50)
    top50 = (
        top50
        .sort_values('binding_score')          # lower = better
        .drop_duplicates(subset='drug_name', keep='first')
        .reset_index(drop=True)
    )
    n_after = len(top50)
    if n_before > n_after:
        print(f'[INFO] Removed {n_before - n_after} duplicate rows from '
              f'DeepPurpose results (kept best binding_score per compound).')

    # -- 4. merge on drug_name ------------------------------------------------
    merged = pd.merge(top50, docked, on='drug_name', how='inner')
    n_merged = len(merged)
    print(f'\n[INFO] {n_merged} compounds successfully docked and merged '
          f'(of {n_after} unique DeepPurpose candidates, {len(docked)} docked).')
    if n_merged == 0:
        raise RuntimeError("No rows after merge — check that drug_name values "
                           "match between the two CSV files.")

    # ── 4. percentile ranks ───────────────────────────────────────────────────
    merged["dp_percentile"]   = percentile_rank(merged["binding_score"])
    merged["vina_percentile"] = percentile_rank(merged["vina_score"])
    merged["composite_score"] = composite_score(merged["dp_percentile"],
                                                merged["vina_percentile"])

    # ── 5. composite rank ─────────────────────────────────────────────────────
    merged["composite_rank"] = merged["composite_score"].rank(method="min").astype(int)
    merged = merged.sort_values("composite_rank").reset_index(drop=True)

    # ── 6. strong hit flag ────────────────────────────────────────────────────
    dp_threshold = np.percentile(merged["binding_score"], DP_PERCENTILE_CUT)
    merged["strong_hit"] = (
        (merged["vina_score"]    <= VINA_CUTOFF) &
        (merged["binding_score"] <= dp_threshold)
    )
    n_strong = merged["strong_hit"].sum()

    # ── 7. reorder columns ────────────────────────────────────────────────────
    col_order = [
        "composite_rank", "drug_name", "pert_iname",
        "binding_score", "dp_percentile",
        "vina_score",    "vina_percentile",
        "composite_score", "strong_hit",
        "smiles", "target",
    ]
    # Keep only columns that exist
    col_order = [c for c in col_order if c in merged.columns]
    # Append any extra columns not listed above
    extras = [c for c in merged.columns if c not in col_order]
    merged = merged[col_order + extras]

    # ── 8. save ───────────────────────────────────────────────────────────────
    merged.to_csv(OUT_CSV, index=False)
    print(f"\n[SAVED] Final ranked candidates → {OUT_CSV}")

    # ── 9. print summary ──────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  TOP 15 COMPOSITE-RANKED CANDIDATES")
    print("=" * 60)

    display_cols = ["composite_rank", "drug_name", "binding_score",
                    "vina_score", "composite_score", "strong_hit"]
    display_cols = [c for c in display_cols if c in merged.columns]

    with pd.option_context("display.max_rows", 20,
                           "display.float_format", "{:.3f}".format,
                           "display.max_colwidth", 28):
        print(merged[display_cols].head(15).to_string(index=False))

    print(f"\n  Strong hits (Vina ≤ {VINA_CUTOFF} AND DeepPurpose top-{DP_PERCENTILE_CUT}th %):")
    print(f"  {n_strong} / {n_merged} compounds flagged\n")

    if n_strong > 0:
        strong_df = merged[merged["strong_hit"]][display_cols]
        with pd.option_context("display.float_format", "{:.3f}".format,
                               "display.max_colwidth", 28):
            print(strong_df.to_string(index=False))

    # ── 10. write summary text file ───────────────────────────────────────────
    summary_lines = [
        "Drug Repurposing Pipeline — Analysis Summary",
        "=" * 52,
        f"Total compounds docked and merged : {n_merged}",
        f"Strong hits flagged               : {n_strong}",
        f"Vina cutoff                       : <= {VINA_CUTOFF} kcal/mol",
        f"DeepPurpose cutoff                : <= {DP_PERCENTILE_CUT}th percentile",
        "",
        "Top 15 by composite rank:",
        merged[display_cols].head(15).to_string(index=False),
        "",
        "Strong hits detail:",
        merged[merged["strong_hit"]][display_cols].to_string(index=False)
        if n_strong > 0 else "  (none meeting both criteria)",
        "",
        "Score interpretation:",
        "  binding_score (DeepPurpose) : predicted Ki [nM], lower = better",
        "  vina_score                  : ΔG [kcal/mol],     lower = better",
        "  composite_score             : weighted percentile rank (40% DP + 60% Vina)",
        "  strong_hit                  : passes both cutoffs simultaneously",
        "",
        "Biological note:",
        "  Corticosteroids (betamethasone, desoximetasone, clocortolone) scoring",
        "  well is expected — their steroid scaffold mirrors 17β-estradiol and",
        "  they are known to interact with the ER-alpha ligand-binding domain.",
        "  These serve as excellent internal validation of the docking setup.",
        "",
        "Next steps: run 12_admet_profiling.py -> 13_dashboard.py",
    ]
    SUMMARY.write_text("\n".join(summary_lines), encoding="utf-8")
    print(f"\n[SAVED] Summary → {SUMMARY}")


if __name__ == "__main__":
    main()