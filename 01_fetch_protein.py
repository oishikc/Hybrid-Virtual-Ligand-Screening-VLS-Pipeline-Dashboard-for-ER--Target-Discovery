import requests
import os

os.makedirs("data", exist_ok=True)

PDB_ID = "1ERE"
url = f"https://files.rcsb.org/download/{PDB_ID}.pdb"

response = requests.get(url)

if response.status_code == 200:
    with open(f"data/{PDB_ID}.pdb", "w") as f:
        f.write(response.text)
    print(f"Success — saved data/1ERE.pdb")
    print(f"File size: {len(response.text):,} characters")
else:
    print(f"Failed — status code {response.status_code}")