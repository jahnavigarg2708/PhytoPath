import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_compounds(plant_name):
    """
    Given a plant's scientific name, returns a DataFrame of all its known 
    phytochemicals from IMPPAT, including plant part and IMPPAT ID.
    """
    url = f"https://cb.imsc.res.in/imppat/phytochemical/{plant_name.replace(' ', '%20')}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table")
    if not tables:
        print(f"No compound table found for {plant_name}")
        return pd.DataFrame()

    rows = tables[0].find_all("tr")
    data = []

    for row in rows[1:]:  # skip header row
        cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) >= 4:
            data.append({
                "plant": cells[0],
                "plant_part": cells[1],
                "impphy_id": cells[2],
                "compound_name": cells[3]
            })

    df = pd.DataFrame(data)
    print(f"Found {len(df)} compounds for {plant_name}")
    return df

def get_smiles(compound_id):
    """
    Given an IMPPAT phytochemical ID, returns its SMILES string.
    """
    url = f"https://cb.imsc.res.in/imppat/phytochemical-detailedpage/{compound_id}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    smiles_label = soup.find(string=lambda text: text and "SMILES" in text)
    if smiles_label:
        br_tag = smiles_label.find_next("br")
        return br_tag.next_sibling.get_text(strip=True)
    return None


def add_smiles(compounds_df, max_compounds=20):
    """
    Given a DataFrame from get_compounds(), fetches SMILES for each compound
    (up to max_compounds) and adds it as a new column.
    """
    df = compounds_df.head(max_compounds).copy()
    smiles_list = []
    
    for index, row in df.iterrows():
        print(f"Fetching SMILES for {row['compound_name']} ({row['impphy_id']})...")
        smiles_list.append(get_smiles(row["impphy_id"]))
        time.sleep(1)
    
    df["SMILES"] = smiles_list
    return df

# Quick test, only runs when this file is executed directly
if __name__ == "__main__":
    tulsi_df = get_compounds("Ocimum tenuiflorum")
    tulsi_root = tulsi_df[tulsi_df["plant_part"] == "root"]
    tulsi_with_smiles = add_smiles(tulsi_root, max_compounds=5)
    print(tulsi_with_smiles)