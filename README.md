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
   SwissTargetPrediction (via Selenium) and retrieves its top predicted human protein 
   targets.
3. **Disease association** ✅ — given a condition name, retrieves associated 
   protein-coding genes from GeneCards, ranked by relevance. Currently limited to 
   GeneCards' default result page size (~20 genes) due to anti-bot protection on their 
   expanded-results API; a fix for this is a known open item.
4. **Overlap analysis** ✅ — cross-references predicted compound targets against 
   disease-associated genes to surface candidates.
5. **Interface** 🔄 in progress — Streamlit app. Plant selection, plant-part selection, 
   compound count control (with time estimate), and live-progress target prediction are 
   built and working. Disease input and overlap display are the next pieces.
6. **Network visualisation** — planned (in-app Python-based visualisation, plus optional 
   downloadable Cytoscape-compatible file).
7. **Revisitable results links** — planned.
8. **Docking** — on hold, pending coursework this semester.

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