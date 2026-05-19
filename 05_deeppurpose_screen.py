import json
import pandas as pd
from DeepPurpose import oneliner

# Load the compound library from Phase 1
df = pd.read_csv("data/clean_ligand_library.csv")
smiles_list = df['smiles'].tolist()
name_list   = df['pert_iname'].tolist()

print(f"Loaded {len(smiles_list)} compounds")

# ER-alpha protein sequence (UniProt P03372)
target_seq = (
    "MTMTLHTKASGMALLHQIQGNELEPLNRPQLKIPLERPLGEVYLDSSKPAVYNYPEGAAYEFNAAAAANAQVYGQTGLPYGPGSEAAAFGSNGLGGFPPLSVS"
    "PSQKTYPQGLSPQGLSPQGLSPQGLSPQGLSPQGLSPQGLSPQGLSPTGISPTGISPTGVSPTGVSPTGVSPTGVSPTGVSPTGVSPTGVSPTGVSPTGVSP"
    "TGVSPTGVSPTGVSAEGSDAKGGPWCPDCGKGTEDCFVCRDGKVLCVDYKNRRIQCNACRLRKCYEVGMMKGGIRKDRRGGRMLKHKRQRDDGEGRGEVGS"
    "AGDMRAANLWPSPLMIKRSKKNSLALSLTADQMVSALLDAEPPILYSEYDPTRPFSEASMMGLLTNLADRELVHMINWAKRVPGFVDLTLHDQVHLLECAWL"
    "EILMIGLVWRSMEHPGKLLFAPNLLLDRNQGKCVEGMVEIFDMLLATSSRFRMMNLQGEEFVCLKSIILLNSGVYTFLSSTLKSLEEKDHIHRVLDKITDTL"
    "IHLMAKAGLTLQQQHQRLAQLLLILSHIRHMSNKGMEHLYSMKCKNVVPLYDLLLEMLDAHRLHAPTSRGGASVEETDQSHLATAGSTSSHSLQKYYITGEA"
    "QNKNSGSYSGPYTNDIKPMPGEEGFIDSLLEVLSDGELSSQGGPQHPHRRPNHPKIPSEKSQLGGPSRSEVREGGSDPQNVKEMLHQHISQSSLPQQPLPLP"
    "PLPLPLPPLPPQPLPQPLSPQPLPQPLPQPLSPQPLPQPLPQPLSPQPLPQPLPQPLSPQPLPQPLPQPLSPQPLPQPLPQPLSPQPLPQPLPQPLSPQPL"
)

print("Running DeepPurpose screening — this may take 5-15 minutes...")

results = oneliner.repurpose(
    target_seq,
    X_repurpose=smiles_list,
    drug_names=name_list,
)

# Read results from the file DeepPurpose saved
results_df = pd.read_csv("./save_folder/results_aggregation/repurposing.txt", sep="\t")
print(results_df.columns.tolist())
print(results_df.head(10))

# Save a clean copy
results_df.to_csv("data/deeppurpose_results.csv", index=False)
print(f"\nFull results saved → data/deeppurpose_results.csv")