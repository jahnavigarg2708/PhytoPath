from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

def get_disease_genes(condition_name, top_n=20):
    """
    Given a disease/condition name, returns a DataFrame of associated genes
    from GeneCards, filtered to protein-coding genes, sorted by relevance.
    Note: currently limited to GeneCards' default result page size (~20 rows)
    due to anti-bot protection on their expanded-results API.
    """
    url = f"https://www.genecards.org/Search/Keyword?queryString={condition_name}"

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    try:
        alert = driver.switch_to.alert
        alert.accept()
    except:
        pass
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "SearchResultsTable")))
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    results_table = soup.find("table", id="SearchResultsTable")
    driver.quit()

    rows = results_table.find_all("tr")
    data = []
    for row in rows[1:]:
        cells = [cell.get_text(strip=True) for cell in row.find_all(["td", "th"])]
        if len(cells) >= 7:
            data.append({
                "symbol": cells[2], "name": cells[3], "type": cells[4],
                "relevance_score": cells[5], "knowledge_score": cells[6]
            })

    df = pd.DataFrame(data)
    df = df[df["type"] == "Protein Coding"]
    df["relevance_score"] = pd.to_numeric(df["relevance_score"], errors="coerce")
    df = df.sort_values("relevance_score", ascending=False).head(top_n).reset_index(drop=True)
    from uniprot_lookup import get_uniprot_id
    
    print("Looking up UniProt IDs for each gene...")
    uniprot_ids = []
    for symbol in df["symbol"]:
        uniprot_ids.append(get_uniprot_id(symbol))
    df["uniprot_id"] = uniprot_ids

    print(f"Found {len(df)} protein-coding genes for '{condition_name}'")
    return df


if __name__ == "__main__":
    anxiety_genes = get_disease_genes("anxiety")
    print(anxiety_genes.head(10))