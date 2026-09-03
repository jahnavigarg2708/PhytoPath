import streamlit as st
from get_compounds import get_compounds

st.title("PhytoPath")
st.write("A computational pipeline for medicinal-plant target-prioritisation analysis.")

plant_name = st.text_input("Enter a plant's scientific name", placeholder="e.g. Withania somnifera")

if st.button("Fetch compounds"):
    with st.spinner(f"Retrieving compounds for {plant_name}..."):
        compounds_df = get_compounds(plant_name)
    
    if compounds_df.empty:
        st.error("No compounds found for this plant. Check the spelling of the scientific name.")
    else:
        st.session_state["compounds_df"] = compounds_df
        st.success(f"Found {len(compounds_df)} compounds for {plant_name}.")

if "compounds_df" in st.session_state:
    df = st.session_state["compounds_df"]
    part_counts = df["plant_part"].value_counts()
    
    st.subheader("Available plant parts")
    for part, count in part_counts.items():
        st.write(f"- {part if part else '(not specified)'}: {count} compounds")

    available_parts = [p if p else "(not specified)" for p in part_counts.index.tolist()]
    chosen_part = st.selectbox("Which plant part do you want to use?", available_parts)
    
    # Handle the "(not specified)" label matching back to actual blank values
    actual_part = "" if chosen_part == "(not specified)" else chosen_part
    filtered_df = df[df["plant_part"] == actual_part]
    
    st.write(f"{len(filtered_df)} compounds available for '{chosen_part}'")
    
    max_compounds = st.slider(
        "How many compounds to process? (higher = more thorough, but slower — roughly 1 minute per compound)",
        min_value=1, max_value=min(30, len(filtered_df)), value=min(10, len(filtered_df))
    )
    
    st.info(f"Estimated time: approximately {max_compounds} minute(s)")
    
    if st.button("Confirm selection"):
        st.session_state["filtered_df"] = filtered_df.head(max_compounds)
        st.success(f"Locked in {max_compounds} compounds from '{chosen_part}'. Ready for the next step.")

if "filtered_df" in st.session_state:
    st.subheader("Step 2: Run target prediction")
    st.write(f"Ready to process {len(st.session_state['filtered_df'])} compounds.")
    
    if st.button("Run pipeline"):
        from get_compounds import add_smiles
        from get_targets import get_targets
        import pandas as pd
        
        df = st.session_state["filtered_df"]
        
        # Fetch SMILES first
        status = st.empty()
        status.write("Fetching chemical structures (SMILES)...")
        with_smiles = add_smiles(df, max_compounds=len(df))
        
        # Now run target prediction, one compound at a time, with a visible progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        all_results = []
        
        total = len(with_smiles)
        for i, (index, row) in enumerate(with_smiles.iterrows()):
            status_text.write(f"Processing compound {i+1} of {total}: {row['compound_name']}...")
            
            if pd.notna(row["SMILES"]) and row["SMILES"].strip() != "":
                result = get_targets(row["SMILES"], compound_name=row["compound_name"], compound_id=row["impphy_id"])
                if not result.empty:
                    all_results.append(result)
            
            progress_bar.progress((i + 1) / total)
        
        if all_results:
            targets_df = pd.concat(all_results, ignore_index=True)
            st.session_state["targets_df"] = targets_df
            status_text.write("Done!")
            st.success(f"Retrieved {len(targets_df)} predicted targets across {targets_df['compound_name'].nunique()} compounds.")
            st.dataframe(targets_df)
        else:
            st.error("No targets were found. Something may have gone wrong during processing.")

if "targets_df" in st.session_state:
    st.subheader("Step 3: Enter a disease or condition")
    condition_name = st.text_input("Enter a disease/condition", placeholder="e.g. anxiety")

    if st.button("Find associated genes"):
        from get_disease_genes import get_disease_genes

        with st.spinner(f"Retrieving genes associated with '{condition_name}'..."):
            disease_genes_df = get_disease_genes(condition_name)

        if disease_genes_df.empty:
            st.error("No genes found for this condition. Check the spelling, or try a broader term.")
        else:
            st.session_state["disease_genes_df"] = disease_genes_df
            st.success(f"Found {len(disease_genes_df)} protein-coding genes associated with '{condition_name}'.")
            st.dataframe(disease_genes_df)

if "disease_genes_df" in st.session_state:
    st.subheader("Step 4: Find overlapping candidates")

    if st.button("Find overlap"):
        from get_overlap import find_overlap

        targets_df = st.session_state["targets_df"]
        disease_genes_df = st.session_state["disease_genes_df"]

        overlap_df = find_overlap(targets_df, disease_genes_df)

        if overlap_df.empty:
            st.warning("No overlapping targets found. Try a different plant part, a larger compound count, or a different condition.")
        else:
            st.success(f"Found {len(overlap_df)} matching compound-target pairs, across {overlap_df['common_name'].nunique()} genes and {overlap_df['compound_name'].nunique()} compounds.")
            st.dataframe(overlap_df)