import streamlit as st
import pandas as pd
from get_compounds import get_compounds, add_smiles
from get_targets import get_targets
from get_disease_genes import get_disease_genes
from get_overlap import find_overlap
from cache import load_cache, save_cache

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

    actual_part = "" if chosen_part == "(not specified)" else chosen_part
    filtered_df = df[df["plant_part"] == actual_part]

    st.write(f"{len(filtered_df)} compounds available for '{chosen_part}'")

    max_compounds = st.slider(
        "How many compounds to process? (higher = more thorough, but slower — roughly 1 minute per compound)",
        min_value=1, max_value=min(30, len(filtered_df)), value=min(10, len(filtered_df))
    )

    st.info(f"Estimated time: approximately {max_compounds} minute(s), unless cached")

    st.subheader("Step 2: Run target prediction")

    if st.button("Run pipeline"):
        selected_df = filtered_df.head(max_compounds)
        st.session_state["filtered_df"] = selected_df

        cache_key = f"targets::{plant_name}::{chosen_part}::{max_compounds}"
        cached_result = load_cache(cache_key)

        if cached_result is not None:
            st.info("Loaded previously computed results from cache — instant.")
            targets_df = cached_result
            st.session_state["targets_df"] = targets_df
            st.success(f"Retrieved {len(targets_df)} predicted targets across {targets_df['compound_name'].nunique()} compounds.")
            st.dataframe(targets_df)
        else:
            status = st.empty()
            status.write("Fetching chemical structures (SMILES)...")
            with_smiles = add_smiles(selected_df, max_compounds=len(selected_df))

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
                save_cache(cache_key, targets_df)
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
        targets_df = st.session_state["targets_df"]
        disease_genes_df = st.session_state["disease_genes_df"]

        overlap_df = find_overlap(targets_df, disease_genes_df)
        st.session_state["overlap_df"] = overlap_df

        if overlap_df.empty:
            st.warning("No overlapping targets found. Try a different plant part, a larger compound count, or a different condition.")
        else:
            st.success(f"Found {len(overlap_df)} matching compound-target pairs, across {overlap_df['common_name'].nunique()} genes and {overlap_df['compound_name'].nunique()} compounds.")
            st.dataframe(overlap_df)

if "overlap_df" in st.session_state and not st.session_state["overlap_df"].empty:
    st.subheader("Step 5: Network visualization")

    if st.button("Generate network diagram"):
        from network_viz import build_network
        import streamlit.components.v1 as components
        import tempfile

        net = build_network(st.session_state["overlap_df"])

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        net.save_graph(temp_file.name)
        html_content = open(temp_file.name, "r", encoding="utf-8").read()

        components.html(html_content, height=620)

        edge_list = st.session_state["overlap_df"][["compound_name", "common_name", "probability"]].rename(
            columns={"compound_name": "source", "common_name": "target", "probability": "weight"}
        )
        csv_data = edge_list.to_csv(index=False)

        st.download_button(
            "Download network as CSV (importable into Cytoscape)",
            data=csv_data,
            file_name="phytopath_network.csv",
            mime="text/csv"
        )