from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time
import os


def get_disease_genes(condition_name, top_n=50):
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
        url = f"https://www.genecards.org/Search/Keyword?queryString={condition_name}"
        driver.get(url)

        try:
            alert = driver.switch_to.alert
            alert.accept()
        except:
            pass

        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.ID, "SearchResultsTable"))
        )
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        results_table = soup.find("table", id="SearchResultsTable")

        if results_table is None:
            print(f"GeneCards result table not found for '{condition_name}'.", flush=True)
            return pd.DataFrame()

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
        if df.empty:
            return df

        df = df[df["type"] == "Protein Coding"]
        df["relevance_score"] = pd.to_numeric(df["relevance_score"], errors="coerce")
        df = df.sort_values("relevance_score", ascending=False).head(top_n).reset_index(drop=True)

        from uniprot_lookup import get_uniprot_id
        df["uniprot_id"] = [get_uniprot_id(s) for s in df["symbol"]]

        print(f"Found {len(df)} protein-coding genes for '{condition_name}'", flush=True)
        return df

    except Exception as e:
        print(f"GeneCards fetch failed for '{condition_name}': {e}", flush=True)
        return pd.DataFrame()

    finally:
        driver.quit()


if __name__ == "__main__":
    anxiety_genes = get_disease_genes("anxiety")
    print(anxiety_genes.head(10))