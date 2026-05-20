# Hybrid Virtual Ligand Screening (VLS) Pipeline & Dashboard for ER-α Target Discovery

An interactive, end-to-end computational drug discovery platform that integrates machine learning and physics-based 3D molecular docking to repurpose FDA-approved compounds for hormone receptor-positive breast cancer treatment.

---

## Project Overview

This platform presents results from a hybrid virtual ligand screening (VLS) pipeline targeting the **Estrogen Receptor-alpha (ER-α)**, a primary driver in approximately 75% of all breast cancer cases. By systematically screening FDA-approved drugs against the resolved crystal structure (**PDB: 1ERE**), this project identifies drug repurposing candidates—approved compounds that may exhibit previously unreported ER-α antagonism.

### Motivation
* **Accelerated Time-to-Clinic:** Drug repurposing leverages known safety profiles and human pharmacokinetics to bypass early clinical trial phases. Traditional *de novo* drug discovery takes 10–15 years; repurposing shortens this timeline substantially.
* **Cost-Effective Hypothesis Generation:** Computational screening enables rapid, low-cost screening of massive chemical libraries before moving to expensive wet-lab validation.

### Datasets & Models
* **Library:** The Broad Institute's FDA-approved drug library (2,057 compounds).
* **Machine Learning:** Binding affinity ($K_i$, nM) predicted via **DeepPurpose's MPNN-CNN** architecture.
* **Molecular Docking:** Top ML candidates re-scored via **AutoDock Vina** 3D molecular docking against the PDB 1ERE binding pocket.
* **Cheminformatics:** Full ADMET profiling and descriptor calculation handled via **RDKit**.

---

## Pipeline & Screening Workflow
[2,057 FDA Drugs] ➔ [1. Prep & Sanitization] ➔ [2. DeepPurpose ML] ➔ [3. Quality Filters] ➔ [4. AutoDock Vina] ➔ [5. ADMET Profiling] ➔ [6. Composite Leaderboard]

1. **Library Preparation:** Sourced 2,057 FDA-approved compounds from the Broad Hub. Executed SMILES canonicalization and structural sanitization via RDKit.
2. **ML Affinity Prediction:** Utilized a DeepPurpose MPNN-CNN model to predict binding affinity ($K_i$ in nM) against the ER-α primary sequence.
3. **Candidate Filtering:** Isolated the top 5% of compounds based on ML scores. Screened out false positives using structural flags (PAINS, Alarm-NMR) and Lipinski's Rule of 5 pre-filters.
4. **3D Molecular Docking:** Performed rigid-receptor, flexible-ligand docking using **AutoDock Vina** against the ligand-binding domain of PDB structure 1ERE. Generated 9 distinct conformers per compound to calculate binding free energy ($\text{kcal/mol}$).
5. **ADMET Profiling:** Evaluated drug-likeness and oral bioavailability using RDKit to calculate Molecular Weight (MW), LogP, H-Bond Donors/Acceptors, TPSA, Rotatable Bonds, Fsp3, and QED metrics alongside Veber rule compliance.
6. **Composite Ranking:** Developed a user-adjustable, weighted percentile scoring matrix to combine the machine learning and docking results into a unified metric:

<div align="center">

$$\text{Composite Score} = (w_{\text{DP}} \times \text{DP}_{\text{pct}}) + (w_{\text{Vina}} \times \text{Vina}_{\text{pct}})$$

</div>

---

## Dashboard Features & Architecture

The accompanying interactive dashboard is broken down into five core exploration modules:

* **Overview:** Visualizes the relationship between ML predictions and physical docking scores via an interactive scatter plot, complete with classification breakdowns and dataset-wide correlation statistics.
* **Docking Analysis:** Displays the fully ranked AutoDock Vina results table, docking score distributions, and individual per-compound energy evaluations.
* **ADMET Landscape:** Maps drug-likeness profiles using interactive radar charts, highlighting Lipinski/Veber compliance and the MW vs. LogP chemical space.
* **Top Candidates:** A dynamic, composite leaderboard. Users can use sidebar sliders to adjust the mathematical weights ($w_{\text{DP}}$ and $w_{\text{Vina}}$) in real-time to prioritize AI or physical simulations.
* **Full Data Explorer:** A complete, multi-column searchable and filterable database enabling custom queries and flat-file CSV data export.

---

## Tech Stack

* **Language:** Python 3.9+
* **Cheminformatics & ML:** RDKit, DeepPurpose, PyTorch
* **Docking Engine:** AutoDock Vina
* **Dashboard/UI:** Streamlit, Plotly, Pandas, NumPy

---

## Getting Started

### Prerequisites
Ensure you have Python 3.9+ installed. It is highly recommended to use a Conda environment due to specific RDKit and DeepPurpose dependencies.

### Installation
```bash
# 1. Clone the repository from GitHub
git clone https://github.com/oishikc/er-alpha-vls-dashboard.git

# 2. Move into the project directory
cd er-alpha-vls-dashboard

# 3. Install all necessary computational dependencies
pip install -r requirements.txt

# 4. Launch the interactive Streamlit dashboard
streamlit run app.py
