import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

plant_name = "Withania somnifera"
url = f"https://cb.imsc.res.in/imppat/phytochemical/{plant_name.replace(' ', '%20')}"

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

tables = soup.find_all("table")
print(f"Found {len(tables)} table(s) on the page")

for i, table in enumerate(tables):
    rows = table.find_all("tr")
    print(f"\nTable {i}: {len(rows)} rows")
    if len(rows) > 1:
        cells = [cell.get_text(strip=True) for cell in rows[1].find_all(["td", "th"])]
        print(f"Sample row: {cells}")