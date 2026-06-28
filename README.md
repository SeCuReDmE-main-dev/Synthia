![Bannière](assets/Banner/mix%20banner/mix%20banner%2010.png)

> **Education access note.** Synthia is designed first for students, teachers, schools, and research collaborators who can pair the repo with an AI companion account and a cloud-document account strong enough for file review, Drive/Docs workflows, source mapping, and repeated classification work. A free Gmail or free AI account can still explore the project, but should not be expected to taxonomize or classify large institutional, company, or research corpora at the same depth as an education or professional workspace. Students and educators should verify current official access before the school year: [ChatGPT Education](https://openai.com/chatgpt/education/), [ChatGPT for Teachers](https://help.openai.com/en/articles/12844995-chatgpt-for-teachers), [Gemini for Students](https://gemini.google/students/), and [Gemini for Education](https://edu.google.com/intl/ALL_us/ai/gemini-for-education/). Offers, eligibility, free periods, and prices change by country, institution, and date.

# Synthia

Synthia is an educational research codebase for context-preserving lexicon intelligence, biology classification, source traceability, taxonomy memory, and uncertainty-aware classification.

Public site: <https://synthia.securedme.ca/>

Repository: <https://github.com/SeCuReDmE-main-dev/Synthia>

## Conception And Scientific Collaboration

- Jean-Sebastien Beaulieu: lead builder for Synthia's software architecture, implementation, public repository, and ORCID identity: <https://orcid.org/0009-0007-2904-0443>.
- Prof. Hector Fernando Aguilar: scientific co-conceptor for Synthia's taxonomy, systematics, PhyloCode/classification direction, redescription-memory framing, and expert-review boundary.

This credit recognizes scientific conception and taxonomy direction. It does not transfer software authorship, formal nomenclatural authority, or autonomous scientific decision-making to Synthia.

## Public Invariant

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

This is Synthia's lexicon-classification chain. `H_lex` is lexicon entropy, `G_lex` is lexicon decision-gap uncertainty, and `I_lexicon` is the context-preserving indeterminacy state used for classification, filtration, switching, and review.

## Plithogenic Biology And System Math

Synthia separates pure engine math from system math. The pure engine math layer contains bounded neutrosophic and plithogenic operators: `T/I/F` values, contradiction load, probability load, dominant attribute values, rough boundary regions, and deterministic projections into the public chain. Those operators are useful by themselves, but biology changes their role. When the object is a species, a taxonomic memory record, a food-safety signal, a conservation concern, a public-health review packet, a geography/ecology context, or an expert disagreement, Synthia is no longer treating math as an isolated abstract engine. It is calling that math inside a living `I_system^S`.

In this framing, plithogenic biology is `I -> I_system^S` in action. A biological object is not just an abstract vector with attributes; it is a source-linked, expert-reviewed, socially consequential system where the same mathematical values can have different meanings depending on context. A high contradiction load in a symbolic algebra exercise is one kind of system signal. A high contradiction load around a taxon, a milk batch, a habitat observation, or a disease-susceptibility review is another kind of system signal because it changes who must review the packet, what evidence must remain visible, and which authority boundary must be preserved. Synthia therefore keeps contradiction load, probability load, rough boundary region, `H_lex`, `G_lex`, and `I_lexicon` visible instead of collapsing them into a single confidence score.

Phase 1 added phylo-plithogenic review packets: phylogenetic and taxonomic identity remains the anchor, while plithogenic contradiction describes review uncertainty around morphology, geography, ecology, disease susceptibility, and expert disagreement. Phase 2 adds uncertainty-aware societal risk triage: food safety, conservation, public health, environmental signals, and taxonomy review can be modeled as system-level review cases with rough regions and probability-aware contradiction. Phase 3 adds a plithogenic biology graph review layer: biological review situations can now be represented as source-linked nodes, edges, hyperedges, and supervertices, so a treatment, taxon, habitat, outcome, expert disagreement, or risk case can remain visible as part of the same `I_system^S` instead of being flattened into a single score. Phase 4 adds a molecular sequence evidence guardrail: compact BLAST-like similarity summaries, NCBI Datasets-like taxon/genome anchors, and Ensembl-like annotation references can be scored as bounded review evidence while raw alignments, long sequence dumps, and live network calls stay outside the core. Phase 5 adds an algorithmic behavior guardrail: parameter choices such as objective family, regularization, validation folds, stopping criteria, encoding, sampling, and reproducibility are treated as visible conditions on biological interpretation. They do not guarantee model performance, prove a biological conclusion, or create taxonomic, diagnostic, conservation, public-health, or nomenclatural authority. Phase 6 adds a scientific governance and evidence-reporting layer: Synthia can now assemble model-card-like summaries, dataset-sheet-style provenance, FAIR-style metadata visibility, validation status, intended-use boundaries, and evidence-gap load for Phase 1-5 outputs. Phase 7 adds a scientific provenance and research-object export layer: Synthia can map PROV-O-style entities, activities, and agents; RO-Crate-style research-object manifests; DataCite and Citation File Format citation metadata; CRediT contributor roles; Academia.edu-style free-platform posts; institutional repository deposits such as DSpace/DASH-style records; and Crossref-style DOI registry metadata. This layer is deliberately strict about evidence class boundaries: a visible post is not a repository deposit, a repository deposit is not peer review, DOI metadata is not scientific truth, and contributor-role metadata is not code authorship or formal taxonomic authority. The reporting improves traceability and review readiness, but it does not certify scientific truth, regulatory validity, diagnostic authority, formal taxonomy, copyright reuse, or autonomous conclusions. Together, these phases make biological, molecular, algorithmic, governance, and publication-chain parts of `I_system^S` inspectable before a specialist interprets any output.

This section is intentionally kept in the README before the public website is updated. It records the implementation doctrine: Synthia uses pure neutrosophic and plithogenic kernels as reusable mathematical engines, but the biology side activates them as system math under `I_system^S`. The project supports education, traceability, triage, and human review. It does not make formal taxonomic acts, food-safety declarations, public-health decisions, conservation orders, environmental hazard declarations, or autonomous scientific conclusions.

## Codebase

The repository contains the local Python research core, tests, public documentation, and static website package for Synthia. The current codebase includes:

- `I_lexicon` nodes, bridges, source evidence, and context-switch traces;
- bounded `T/I/F`, neutrosophic kernels, and plithogenic contradiction profiles;
- biology and taxonomy memory records, phylo-plithogenic review packets, risk-triage cases, biology graph review layers, molecular evidence review cases, algorithmic behavior guardrails, scientific governance reporting packets, research-object provenance packets, citation auditing, and AI-assistance disclosure boundaries;
- simulation-first swarm field-scout records, digital pheromone maps, and safety gates;
- optional RethinkDB memory surfaces for swarm state and HippoRAG-style graph traces;
- a static public website under `web/landing/`.

## Boundary

Synthia is not a production scientific authority, medical tool, environmental deployment system, drone-control platform, or formal nomenclatural authority. It is an educational research project for preserving lexicon context, uncertainty, source traceability, and human-review boundaries.

External code contributions are locked while the base architecture is actively developed. Scientific collaboration and source-review roles can be credited without opening the code contribution policy.

## Development

```powershell
python -m pytest
```
![Bannière](assets/Banner/ASCII%20banner/AScii%20banner(1).png)
No raw private correspondence, authentication caches, restricted manuscript bodies, or credential material should be committed to this repository.
