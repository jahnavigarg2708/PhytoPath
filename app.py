import streamlit as st
import pandas as pd
from pipeline import (
    get_compounds_for_plant,
    get_targets_for_selection,
    get_genes_for_condition,
    compute_overlap,
)
st.set_page_config(page_title="PhytoPath", page_icon="🌿", layout="wide")

def show_table(df):
    display_df = df.reset_index(drop=True)
    display_df.index = display_df.index + 1
    st.dataframe(display_df)

st.title("PhytoPath")
st.write("A computational pipeline for medicinal-plant target-prioritisation analysis.")

with st.sidebar:
    st.header("🌿 PhytoPath")
    st.caption("Medicinal-plant target-prioritisation pipeline")
    plant_name = st.text_input("Plant's scientific name", placeholder="e.g. Withania somnifera")
    fetch_clicked = st.button("Fetch compounds", use_container_width=True)

if fetch_clicked:
    with st.spinner(f"Retrieving compounds for {plant_name}..."):
        compounds_df = get_compounds_for_plant(plant_name)

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

    st.divider()
    st.subheader("🧪 Step 2: Run target prediction")
    if st.button("Run pipeline"):
        selected_df = filtered_df.head(max_compounds)

        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(current, total, name):
            status_text.write(f"Processing compound {current} of {total}: {name}...")
            progress_bar.progress(current / total)

        targets_df, n_cached, n_new = get_targets_for_selection(
            selected_df, plant_name, chosen_part, progress_callback=update_progress
        )

        if n_cached:
            st.info(f"Used {n_cached} cached compound(s), fetched {n_new} new.")

        if not targets_df.empty:
            st.session_state["targets_df"] = targets_df
            st.success("Done!")
        else:
            st.error("No targets were found. Something may have gone wrong during processing.")

    if "targets_df" in st.session_state:
        tdf = st.session_state["targets_df"]
        st.write(f"Currently holding {len(tdf)} predicted targets across {tdf['compound_name'].nunique()} compounds.")
        show_table(tdf)

if "targets_df" in st.session_state:
    st.divider()
    st.subheader("🦠 Step 3: Enter a disease or condition")
    condition_name = st.text_input("Enter a disease/condition", placeholder="e.g. anxiety")

    if st.button("Find associated genes"):
        with st.spinner(f"Retrieving genes associated with '{condition_name}'..."):
            disease_genes_df = get_genes_for_condition(condition_name)

        if disease_genes_df.empty:
            st.error("No genes found for this condition. Check the spelling, or try a broader term.")
        else:
            st.session_state["disease_genes_df"] = disease_genes_df

    if "disease_genes_df" in st.session_state:
        ddf = st.session_state["disease_genes_df"]
        st.write(f"Currently holding {len(ddf)} protein-coding genes.")
        show_table(ddf)

if "disease_genes_df" in st.session_state:
    st.divider()
    st.subheader("🦠 Step 4: Find overlapping candidates")

    if st.button("Find overlap"):
        overlap_df = compute_overlap(st.session_state["targets_df"], st.session_state["disease_genes_df"])
        st.session_state["overlap_df"] = overlap_df

        if overlap_df.empty:
            st.warning("No overlapping targets found. Try a different plant part, a larger compound count, or a different condition.")

    if "overlap_df" in st.session_state and not st.session_state["overlap_df"].empty:
        odf = st.session_state["overlap_df"]
        st.write(f"Currently holding {len(odf)} matching compound-target pairs, across {odf['common_name'].nunique()} genes and {odf['compound_name'].nunique()} compounds.")
        show_table(odf)

if "overlap_df" in st.session_state and not st.session_state["overlap_df"].empty:
    st.divider()
    st.subheader("🕸️ Step 5: Network visualization")

    if st.button("Generate network diagram"):
        from network_viz import build_network
        import tempfile

        net = build_network(st.session_state["overlap_df"])
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        net.save_graph(temp_file.name)
        st.session_state["network_html"] = open(temp_file.name, "r", encoding="utf-8").read()

    if "network_html" in st.session_state:
        import streamlit.components.v1 as components
        components.html(st.session_state["network_html"], height=620)

        edge_list = st.session_state["overlap_df"][["compound_name", "common_name", "probability"]].rename(
            columns={"compound_name": "source", "common_name": "target", "probability": "weight"}
        )
        st.download_button(
            "Download network as CSV (importable into Cytoscape)",
            data=edge_list.to_csv(index=False),
            file_name="phytopath_network.csv",
            mime="text/csv"
        )