# PhytoPath — Product Requirements Document

## 1. Overview
PhytoPath is a general-purpose, deployed computational pipeline and web tool for 
medicinal-plant phytochemical–target–disease association analysis. Given any 
medicinal plant and any disease/condition, it automates compound retrieval, target 
prediction, disease-gene retrieval, candidate overlap analysis, and network 
visualisation.

## 2. Problem Statement
Network pharmacology analyses of medicinal plants are typically manual, one-time, 
single-plant exercises. The underlying workflow is reusable in principle but rarely 
implemented as reusable software. PhytoPath addresses this by building and deploying 
a working, general-purpose pipeline rather than a single case study.

## 3. Target Users
Researchers, students, and academics investigating the possible molecular basis of 
traditional medicinal plant use — a hypothesis-generation tool, not a diagnostic or 
clinical decision-making tool.

## 4. System Architecture

### 4.1 Data flow
Plant name → IMPPAT → Compounds + plant parts + SMILES
↓
SwissTargetPrediction → Predicted targets (+ UniProt ID)

Condition name → GeneCards → Disease genes → UniProt ID mapping
↓
UniProt-ID-based overlap analysis
↓
Network visualisation + Cytoscape CSV export

### 4.2 Modules
| Module | Responsibility |
|---|---|
| `get_compounds.py` | IMPPAT compound + SMILES retrieval |
| `get_targets.py` | SwissTargetPrediction automation, with retry/backoff |
| `get_disease_genes.py` | GeneCards retrieval + UniProt mapping, with retry/backoff |
| `uniprot_lookup.py` | UniProt REST API gene→accession-ID lookup |
| `network_viz.py` | Interactive network diagram (pyvis) |
| `cache.py` | Per-compound local result caching |
| `pipeline.py` | Core orchestration layer; single source of truth for pipeline logic |
| `app.py` | Streamlit interface; calls `pipeline.py`, handles display and session state |

### 4.3 Tech stack
Python, pandas, BeautifulSoup, Selenium (headless, cloud-hardened), Streamlit, pyvis, 
requests.

### 4.4 Data sources
IMPPAT, SwissTargetPrediction, GeneCards, UniProt REST API (DisGeNET planned).

### 4.5 Deployment
Live on Streamlit Community Cloud. Chromium installed via `packages.txt`; headless 
Chrome configured with `--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu`; 
Chromium binary path set conditionally (checked via `os.path.exists`) so identical 
code runs correctly on local Windows/Mac development environments and the cloud's 
Linux environment without modification.

## 5. Current Status
Deployed, functional prototype. All core pipeline stages implemented and validated 
end-to-end, including UniProt-ID-based overlap matching, per-compound caching, 
in-app network visualisation, and cloud deployment. Input validation and correct 
session-state invalidation (changing an upstream input clears stale downstream 
results) are implemented.

## 6. Known Limitations
- GeneCards and SwissTargetPrediction automation show intermittent failures 
  specifically under cloud deployment (not reproduced locally), most plausibly due to 
  bot-detection on shared cloud IP ranges. Mitigated via retry logic with exponential 
  backoff (up to 5 attempts); not fully eliminated. This is documented as an 
  observed, measured limitation (approx. 50% of GeneCards calls required a retry 
  across an 11-run sample), not a hidden defect.
- GeneCards results capped at ~17–20 genes (default page size); their 
  expanded-results API is protected against automated access.
- Single disease-gene source currently in production; DisGeNET integration pending 
  account approval (follow-up requested).
- Local, non-shared caching.
- No fallback/alternative data source per step (future direction, not current scope).

## 7. Roadmap (priority order)
1. DisGeNET integration as a second, independent, API-based disease-gene source 
   (also expected to improve reliability over scraping-based GeneCards retrieval)
2. Formal algorithm specification for publication (per supervisor's request)
3. Systematic validation with reported statistics across multiple plant/condition 
   pairs (per supervisor's request, in the absence of directly comparable prior 
   literature for some pairs)
4. Revisitable results links (unique URL per run)
5. Optional: plant-part therapeutic-use context display (IMPPAT already contains 
   this data; suggested by ICGEB guest faculty as a way to support users without 
   prior domain research — not an AI/chatbot feature)
6. Streamlit UI visual polish

## 8. Publication Plan
Supervisor (Prof. Mansaf Alam) has offered to co-author and support publication of 
this work. Two specific guidance points given:
- Include a formal algorithm specification of the pipeline (structured 
  pseudocode/stepwise description), not only a narrative description.
- Where directly comparable prior literature is unavailable for a given 
  plant/condition pairing, support claims with the project's own statistical/ 
  quantitative evidence (e.g. validation results across multiple runs and 
  plant/condition pairs) rather than external citation alone.

## 9. Explicitly Out of Scope (this semester)
Molecular docking, AI/LLM-based result interpretation or chatbot features, wet-lab 
validation, fallback/alternative-tool layers per pipeline step, shared/multi-user 
caching infrastructure.

## Author
Jahnavi Garg, MSc Bioinformatics, Jamia Millia Islamia
Supervisor: Prof. Mansaf Alam