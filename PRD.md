# PhytoPath — Product Requirements Document

## 1. Overview
PhytoPath is a general-purpose computational pipeline and interactive tool for 
medicinal-plant phytochemical–target–disease association analysis. Given any 
medicinal plant and any disease/condition, it automates the retrieval of bioactive 
compounds, prediction of likely human protein targets, retrieval of disease-associated 
genes, and identification of candidate compound–target–disease associations — 
packaged behind a web interface.

## 2. Problem Statement
Network pharmacology analyses of medicinal plants are typically conducted manually, 
one plant and one condition at a time, with no reusable tooling. PhytoPath addresses 
this by automating the full workflow as reusable software, applicable to any 
plant/disease pair rather than a single case study.

## 3. Target Users
Researchers, students, and academics investigating the possible molecular basis of 
traditional medicinal plant use — a starting-point hypothesis-generation tool, not a 
diagnostic or clinical decision-making tool.

## 4. System Architecture

### 4.1 Data flow
Plant name → IMPPAT → Compounds + plant parts + SMILES
↓
SwissTargetPrediction → Predicted protein targets (+ UniProt ID)

Disease/condition name → GeneCards (+ DisGeNET, planned) → Disease-associated genes
↓
Overlap analysis (UniProt-ID-based matching)
↓
Network visualisation + CSV/Cytoscape export

### 4.2 Modules
| Module | Responsibility |
|---|---|
| `get_compounds.py` | Retrieves plant phytochemicals and SMILES from IMPPAT |
| `get_targets.py` | Automates SwissTargetPrediction submission and result parsing |
| `get_disease_genes.py` | Retrieves disease-associated genes from GeneCards |
| `get_overlap.py` | Cross-references targets against disease genes |
| `network_viz.py` | Builds interactive network diagram (pyvis) |
| `cache.py` | Local result caching to avoid redundant external queries |
| `pipeline.py` | Core orchestration logic (plant + condition → results) |
| `app.py` | Streamlit interface layer, calls `pipeline.py` |

### 4.3 Tech stack
Python, pandas, BeautifulSoup, Selenium (headless), Streamlit, pyvis, requests.

### 4.4 External data sources
IMPPAT, SwissTargetPrediction, GeneCards (DisGeNET planned).

## 5. Current Status (as of this version)
Functional working prototype. Core pipeline validated end-to-end across multiple 
plant/disease pairs (Withania somnifera/anxiety, Ocimum tenuiflorum/diabetes). 
Compound retrieval, target prediction, disease association, overlap analysis, caching, 
and network visualisation are implemented and working.

## 6. Known Limitations
- GeneCards results capped at ~17–20 genes (default page size); their expanded-results 
  API is protected against automated access.
- Overlap matching currently uses gene-symbol text comparison; being upgraded to 
  UniProt-ID-based matching for scientific rigour.
- Single disease-gene source (GeneCards); DisGeNET planned as a second, independent 
  source for cross-validation.
- `app.py` currently duplicates some pipeline logic rather than calling `pipeline.py` 
  directly; architectural cleanup planned.
- No fallback/alternative data source per step yet if a given external tool is 
  unavailable; noted as a future direction, not in current scope.
- Caching is currently local to the machine running the app (file-based), not shared 
  across deployments or users.

## 7. Roadmap (priority order)
1. DisGeNET integration as a second disease-gene source
2. Streamlit UI visual polish
3. Broader validation across additional plant/condition pairs
4. Revisitable results links (unique URL per run)

## 8. Explicitly Out of Scope (this semester)
Molecular docking, fallback/alternative-tool layers per pipeline step, AI-generated 
result interpretation, wet-lab validation.

## Author
Jahnavi Garg, MSc Bioinformatics, Jamia Millia Islamia
Supervisor: Prof. Mansaf Alam