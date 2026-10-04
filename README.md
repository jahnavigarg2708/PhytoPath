# PhytoPath

A reusable computational pipeline and interactive web tool for medicinal-plant 
phytochemical–target–disease association analysis. Given any medicinal plant and any 
disease/condition, PhytoPath automates compound retrieval, target prediction, 
disease-gene association, candidate overlap analysis, and network visualisation — 
rather than performing a single manual, plant-specific case study.

**Live tool:** [phytopath.streamlit.app](https://phytopath.streamlit.app)

## Background
This project builds on the author's BSc dissertation (rbcL-based taxonomic 
classification of ten Ayurvedic plants, Delhi University) and an earlier single-plant 
case study (Withania somnifera and anxiety-related targets). PhytoPath generalises 
that case study into reusable software, following explicit guidance from the project 
supervisor (Prof. Mansaf Alam, Dept. of Computer Science, JMI) to build a tool.

## Pipeline stages
1. **Compound retrieval** ✅ — given a plant name, retrieves its full phytochemical 
   profile from IMPPAT (all plant parts, in one request), including SMILES structures. 
   Validated across multiple unrelated plants (Withania somnifera, Ocimum tenuiflorum, 
   Ocimum americanum).
2. **Target prediction** ✅ — automates submission of each compound's SMILES to 
   SwissTargetPrediction (headless Selenium), returning ranked predicted human protein 
   targets. Includes explicit element-wait logic and retry with exponential backoff to 
   handle variable cloud-server response times.
3. **Disease association** ✅ — given a condition name, retrieves associated 
   protein-coding genes from GeneCards (headless Selenium), each mapped to a UniProt 
   accession ID via the UniProt REST API. Includes retry logic with exponential 
   backoff to handle intermittent failures (see Known Limitations).
4. **Overlap analysis** ✅ — cross-references predicted compound targets against 
   disease-associated genes using stable UniProt accession IDs (not text/symbol 
   matching), for scientifically defensible identifier matching.
5. **Interface** ✅ — Streamlit app: plant selection with plant-part and compound-count 
   control (with time estimate), live-progress target prediction, disease input, 
   overlap results, all running headless. Input validation prevents empty submissions. 
   Changing an upstream input (plant, compound count, condition) correctly clears all 
   downstream results rather than leaving stale data displayed.
6. **Caching** ✅ — per-compound local caching; repeated or partially-overlapping 
   compound selections reuse cached results rather than re-querying external servers.
7. **Network visualisation** ✅ — interactive compound–target network diagram rendered 
   in-app (via pyvis), plus a downloadable CSV export compatible with Cytoscape.
8. **Deployment** ✅ — live on Streamlit Community Cloud. Required cloud-specific 
   hardening: Chromium installed via `packages.txt`; headless Chrome launched with 
   `--no-sandbox`, `--disable-dev-shm-usage`, `--disable-gpu`; binary path set 
   conditionally so the same code runs correctly both locally (Windows/Mac) and on 
   the cloud's Linux environment.
9. **Revisitable results links** *(planned)* — unique, shareable link per run.
10. **DisGeNET integration** *(pending)* — second, independent disease-gene source via 
    documented REST API; account approval requested, awaiting response.
11. **Docking** — explicitly not part of this semester's project scope.

## Key preliminary finding (from the earlier case study)
Two Withania somnifera compounds (Hygrine, Cuscohygrine) were predicted to target 
**HTR1A** (serotonin receptor 1A), a clinically validated anxiolytic drug target 
(e.g. buspirone). This is a computationally predicted association, not evidence of 
clinical efficacy, and is treated as a hypothesis for further investigation rather 
than a confirmed result.

## Known limitations
- **GeneCards and SwissTargetPrediction retrieval, implemented via browser automation, 
  experience intermittent failures when deployed on cloud infrastructure** — likely 
  due to bot-detection measures affecting shared cloud IP ranges, observed as 
  inconsistent timeouts not reproducible locally. Retry logic with exponential backoff 
  (up to 5 attempts) mitigates but does not eliminate this; across an 11-run sample, 
  roughly half required more than one attempt. DisGeNET, via a documented API rather 
  than scraping, is expected to be more reliable once integrated.
- Disease-gene results from GeneCards are limited to their default result-page size 
  (~17–20 genes); their expanded-results API returns 403 errors on automated access.
- Caching is local to the running instance, not shared across deployments or users.
- No fallback/alternative data source per pipeline step yet (flagged as a future 
  direction, not current scope).

## Data sources
IMPPAT, SwissTargetPrediction, GeneCards, UniProt (DisGeNET planned)

## Tools used
Python, Streamlit, Selenium, BeautifulSoup, pandas, pyvis, requests

## Status
Deployed, functional end-to-end prototype. MSc Bioinformatics minor project, Jamia 
Millia Islamia, supervised by Prof. Mansaf Alam.

## Author
Jahnavi Garg