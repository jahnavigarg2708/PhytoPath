import pandas as pd

def find_overlap(targets_df, disease_genes_df):
    """
    Given predicted compound targets and disease-associated genes,
    returns the rows where a predicted target matches a disease gene.
    """
    if targets_df.empty or disease_genes_df.empty:
        print("One of the input tables is empty — nothing to compare.")
        return pd.DataFrame()

    disease_genes = set(disease_genes_df["symbol"].str.strip().str.upper())

    targets_df = targets_df.copy()
    targets_df["common_name_clean"] = targets_df["common_name"].str.strip().str.upper()
    overlap_df = targets_df[targets_df["common_name_clean"].isin(disease_genes)]

    print(f"\nOverlap found: {len(overlap_df)} matching rows")
    print(f"Unique disease-related genes hit: {overlap_df['common_name'].nunique()}")
    print(f"Unique compounds involved: {overlap_df['compound_name'].nunique()}")

    return overlap_df.drop(columns=["common_name_clean"])