import requests

def get_uniprot_id(gene_symbol):
    """
    Given a human gene symbol, returns its primary UniProt accession ID.
    """
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        "query": f"gene:{gene_symbol} AND organism_id:9606 AND reviewed:true",
        "fields": "accession",
        "format": "json",
        "size": 1
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    if data.get("results"):
        return data["results"][0]["primaryAccession"]
    return None


if __name__ == "__main__":
    test_gene = "HTR1A"
    result = get_uniprot_id(test_gene)
    print(f"{test_gene} → {result}")