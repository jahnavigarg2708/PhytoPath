# PhytoPath

A general-purpose computational pipeline for medicinal-plant phytochemical–target–disease 
association analysis. Given any medicinal plant and any disease/condition, PhytoPath 
automates compound retrieval, target prediction, disease-gene association, and candidate 
overlap analysis — packaged behind an interactive interface.

This is a generalisation of an earlier plant-specific analysis (Withania somnifera / 
anxiety), rebuilt as reusable software rather than a single case study.

## Status: work in progress — MSc Bioinformatics minor project, Jamia Millia Islamia
Supervisor: Prof. Mansaf Alam

## Pipeline stages
1. **Compound retrieval** ✅ — given a plant name, retrieves its full phytochemical 
   profile from IMPPAT (all plant parts), including SMILES structures. Tested and 
   confirmed working across multiple, unrelated plants (Withania somnifera, Ocimum 
   tenuiflorum, Ocimum americanum).
2. **Target prediction** ✅ — given a compound's SMILES, automates submission to 
   SwissTargetPrediction (via headless Selenium) and retrieves its top predicted human 
   protein targets.
3. **Disease association** ✅ — given a condition name, retrieves associated 
   protein-coding genes from GeneCards (via headless Selenium), ranked by relevance. 
   Currently limited to GeneCards' default result page size (~17-20 genes) due to 
   anti-bot protection on their expanded-results API.
4. **Overlap analysis** ✅ — cross-references predicted compound targets against 
   disease-associated genes using stable UniProt-ID-based matching (upgraded from 
   earlier gene-symbol text matching, for scientific rigour).
5. **Interface** ✅ — Streamlit app with the full pipeline wired end-to-end: plant 
   selection, plant-part and compound-count control (with time estimate), live-progress 
   target prediction, disease input, and overlap results — all running headless.
6. **Caching** ✅ — repeated runs of the same plant/part/compound-count combination load 
   instantly from a local cache instead of re-querying external servers.
7. **Network visualisation** ✅ — interactive, draggable compound–target network diagram 
   rendered directly in the app (via pyvis), plus a downloadable CSV export compatible 
   with Cytoscape for users who want to explore the network there.
8. **Revisitable results links** *(planned)* — unique, shareable link per run.
9. **Docking** — not part of this semester's project scope.

## Status
Core pipeline complete and working end-to-end via the Streamlit interface, including 
network visualisation, result caching (per-compound, so partial reuse works across 
different compound-count selections), and UniProt-ID-based overlap matching. Pipeline 
logic has been consolidated into `pipeline.py`, with `app.py` calling it directly 
rather than duplicating logic. Revisitable links, DisGeNET integration, and interface 
polish are the next pieces.

## Known limitations
- GeneCards disease-gene retrieval currently capped at ~20 results (default page size); 
  their expanded-results API returned 403 errors during development and needs a proper 
  fix or an alternative approach.
- Overlap matching currently uses gene symbol text matching; upgrading to stable 
  UniProt-ID-based matching is a planned refinement.
- Target prediction takes roughly 1 minute per compound; the interface currently caps 
  and estimates this, but true background/async processing is a future improvement.

## Tools used
Python (pandas, BeautifulSoup, Selenium, requests, Streamlit)

## Data sources
IMPPAT, SwissTargetPrediction, GeneCards

## Author
Jahnavi Garg