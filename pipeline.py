import pandas as pd
from get_compounds import get_compounds, add_smiles
from get_targets import get_targets
from get_disease_genes import get_disease_genes
from get_overlap import find_overlap
from cache import load_compound_cache, save_compound_cache


def get_compounds_for_plant(plant_name):
    """Step 1: retrieve all compounds for a plant."""
    return get_compounds(plant_name)


def get_targets_for_selection(selected_df, plant_name, plant_part, progress_callback=None):
    """
    Step 2: given a selected set of compounds, fetches SMILES and predicted 
    targets for each, using a per-compound cache so partial reuse works 
    regardless of how many compounds are requested in a given run.
    
    progress_callback, if given, is called as progress_callback(current, total, compound_name)
    after each compound is processed, so a caller (e.g. Streamlit) can show live progress.
    """
    cached_pieces = []
    to_fetch = []

    for _, row in selected_df.iterrows():
        cached = load_compound_cache(plant_name, plant_part, row["impphy_id"])
        if cached is not None:
            cached_pieces.append(cached)
        else:
            to_fetch.append(row)

    new_results = []
    if to_fetch:
        to_fetch_df = pd.DataFrame(to_fetch)
        with_smiles = add_smiles(to_fetch_df, max_compounds=len(to_fetch_df))
        total = len(with_smiles)

        for i, (index, row) in enumerate(with_smiles.iterrows()):
            if pd.notna(row["SMILES"]) and row["SMILES"].strip() != "":
                result = get_targets(row["SMILES"], compound_name=row["compound_name"], compound_id=row["impphy_id"])
                if not result.empty:
                    save_compound_cache(plant_name, plant_part, row["impphy_id"], result)
                    new_results.append(result)
            if progress_callback:
                progress_callback(i + 1, total, row["compound_name"])

    all_pieces = cached_pieces + new_results
    if all_pieces:
        return pd.concat(all_pieces, ignore_index=True), len(cached_pieces), len(new_results)
    return pd.DataFrame(), 0, 0


def get_genes_for_condition(condition_name):
    """Step 3: retrieve disease-associated genes for a condition."""
    return get_disease_genes(condition_name)


def compute_overlap(targets_df, disease_genes_df):
    """Step 4: find overlap between predicted targets and disease genes."""
    return find_overlap(targets_df, disease_genes_df)


if __name__ == "__main__":
    # Simple command-line version of the pipeline, useful for quick testing
    plant_name = input("Enter plant name: ").strip()
    compounds_df = get_compounds_for_plant(plant_name)

    if compounds_df.empty:
        print("No compounds found.")
    else:
        print("\nAvailable plant parts:")
        for part, count in compounds_df["plant_part"].value_counts().items():
            print(f"  {part if part else '(not specified)'}: {count}")

        chosen_part = input("\nWhich plant part? ").strip()
        filtered_df = compounds_df[compounds_df["plant_part"] == chosen_part]
        max_compounds = int(input(f"How many of {len(filtered_df)} compounds to process? "))
        selected_df = filtered_df.head(max_compounds)

        def print_progress(current, total, name):
            print(f"[{current}/{total}] {name}")

        targets_df, n_cached, n_new = get_targets_for_selection(selected_df, plant_name, chosen_part, print_progress)
        print(f"\nGot {len(targets_df)} targets ({n_cached} from cache, {n_new} freshly fetched)")

        condition_name = input("\nEnter a disease/condition: ").strip()
        disease_genes_df = get_genes_for_condition(condition_name)

        overlap_df = compute_overlap(targets_df, disease_genes_df)
        print(f"\nFinal overlap:\n{overlap_df}")