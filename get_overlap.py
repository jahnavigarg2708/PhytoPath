import pandas as pd

def find_overlap(targets_df, disease_genes_df):
    """
    Given predicted compound targets and disease-associated genes,
    returns rows where a predicted target's UniProt ID matches a disease gene's
    UniProt ID — a more scientifically rigorous match than comparing text names.
    """
    if targets_df.empty or disease_genes_df.empty:
        print("One of the input tables is empty — nothing to compare.")
        return pd.DataFrame()

    disease_ids = set(disease_genes_df["uniprot_id"].dropna())

    targets_df = targets_df.copy()
    overlap_df = targets_df[targets_df["uniprot_id"].isin(disease_ids)]

    print(f"\nOverlap found (UniProt-ID-based): {len(overlap_df)} matching rows")
    print(f"Unique disease-related genes hit: {overlap_df['common_name'].nunique()}")
    print(f"Unique compounds involved: {overlap_df['compound_name'].nunique()}")

    return overlap_df