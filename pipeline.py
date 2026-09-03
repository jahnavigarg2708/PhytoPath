from get_compounds import get_compounds, add_smiles
from get_targets import get_targets_for_compounds
from get_disease_genes import get_disease_genes
from get_overlap import find_overlap

def run_pipeline(plant_name, condition_name, max_compounds=5):
    print(f"\n=== Step 1: Retrieving compounds for {plant_name} ===")
    compounds_df = get_compounds(plant_name)
    if compounds_df.empty:
        print("No compounds found. Stopping.")
        return None

    part_counts = compounds_df["plant_part"].value_counts()
    print("\nAvailable plant parts:")
    for part, count in part_counts.items():
        print(f"  {part if part else '(not specified)'}: {count} compounds")

    chosen_part = input("\nWhich plant part do you want to use? ").strip()
    filtered_df = compounds_df[compounds_df["plant_part"] == chosen_part]
    print(f"\n{len(filtered_df)} compounds found for plant part '{chosen_part}'")

    print(f"\n=== Step 2: Fetching SMILES structures ===")
    with_smiles = add_smiles(filtered_df, max_compounds=max_compounds)

    print(f"\n=== Step 3: Predicting targets ===")
    targets_df = get_targets_for_compounds(with_smiles, max_compounds=max_compounds)

    print(f"\n=== Step 4: Retrieving genes associated with '{condition_name}' ===")
    disease_genes_df = get_disease_genes(condition_name)

    print(f"\n=== Step 5: Finding overlap ===")
    overlap_df = find_overlap(targets_df, disease_genes_df)

    return overlap_df


if __name__ == "__main__":
    results = run_pipeline("Ocimum tenuiflorum", "diabetes", max_compounds=5)
    print("\n=== Final prioritised candidates ===")
    print(results)