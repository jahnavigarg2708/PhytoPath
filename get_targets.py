from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def get_targets(smiles, compound_name="", compound_id=""):
    """
    Given a compound's SMILES string, submits it to SwissTargetPrediction and 
    returns a DataFrame of its top predicted human protein targets.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    if os.path.exists("/usr/bin/chromium"):
        options.binary_location = "/usr/bin/chromium"
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.swisstargetprediction.ch/")
        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            pass  # no alert present, nothing to do
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.ID, "smilesBox"))
        )
        time.sleep(2)

        smiles_box = driver.find_element(By.ID, "smilesBox")
        smiles_box.clear()
        smiles_box.send_keys(smiles)

        submit_button = driver.find_element(By.ID, "submitButton")
        submit_button.click()

        WebDriverWait(driver, 120).until(EC.url_contains("result.php"))

        soup = BeautifulSoup(driver.page_source, "html.parser")
        table = soup.find("table", {"id": "resultTable"})

        results = []
        if table:
            rows = table.find_all("tr")[1:]  # skip header
            for r in rows:
                cells = [cell.get_text(strip=True) for cell in r.find_all(["td", "th"])]
                if len(cells) >= 6:
                    results.append({
                        "compound_name": compound_name,
                        "compound_id": compound_id,
                        "target": cells[0],
                        "common_name": cells[1],
                        "uniprot_id": cells[2],
                        "chembl_id": cells[3],
                        "target_class": cells[4],
                        "probability": cells[5]
                    })

        return pd.DataFrame(results)

    except Exception as e:
        print(f"  Error processing {compound_name}: {e}", flush=True)
        return pd.DataFrame()

    finally:
        driver.quit()


def get_targets_for_compounds(compounds_df, max_compounds=20):
    """
    Given a DataFrame of compounds (from get_compounds), runs get_targets() 
    on each one and combines all results into a single DataFrame.
    """
    all_results = []
    compounds_to_process = compounds_df.head(max_compounds)
    
    for index, row in compounds_to_process.iterrows():
        print(f"[{index+1}/{len(compounds_to_process)}] Processing {row['compound_name']}...")
        result = get_targets(
            smiles=row.get("SMILES", ""),
            compound_name=row["compound_name"],
            compound_id=row["impphy_id"]
        )
        if not result.empty:
            all_results.append(result)
    
    if all_results:
        return pd.concat(all_results, ignore_index=True)
    return pd.DataFrame()

if __name__ == "__main__":
    test_smiles = "OCC1=C(C)C[C@@H](OC1=O)[C@H]([C@H]1CC[C@@H]2[C@]1(C)CC[C@H]1[C@H]2CCC2=CC(=O)C=C[C@]12C)C"
    
    result = get_targets(test_smiles, compound_name="Withasomidienone", compound_id="IMPHY000630")
    print(result)