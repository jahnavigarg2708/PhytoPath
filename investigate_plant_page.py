import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

plant_name = "Ocimum tenuiflorum"
url = f"https://cb.imsc.res.in/imppat/phytochemical/{plant_name.replace(' ', '%20')}"

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

tables = soup.find_all("table")
print(f"Found {len(tables)} table(s) on the page.")

if tables:
    rows = tables[0].find_all("tr")
    print(f"First table has {len(rows)} rows.")
    if len(rows) > 1:
        print("Sample row:", [cell.get_text(strip=True) for cell in rows[1].find_all(["td", "th"])])
else:
    print("No tables found directly in the HTML — likely loaded via JavaScript.")