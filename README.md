 ![Synthia-identity](./assets/Banner/wide%20banner%205.png)

# Synthia

Synthia is an educational research project for an evolving `I_lexicon`: a context-preserving lexicon and taxonomy core that updates as it learns new classification systems.

The current public mathematical invariant is:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

This is the lexicon-classification chain. `H_lex` is lexicon entropy, `G_lex` is lexicon decision-gap uncertainty, and `I_lexicon` is the final context-preserving indeterminacy state used when Synthia classifies, filters, switches, or quarantines information by lexicon.

Author identifier: Jean-Sebastien Beaulieu, ORCID: https://orcid.org/0009-0007-2904-0443

## Project Status

This repository is currently under active solo development. External contributions are locked while the base architecture, taxonomy model, and public/private documentation boundary are being stabilized.

The public repository contains code, tests, and safe public documentation only. Private source ledgers, Gmail-derived evidence summaries, implementation notes, and the full soul draft live beside this repo in:

```text
..\Synthia_organisation
```

## Educational Purpose

Synthia is not a production scientific authority, medical tool, environmental deployment system, drone-control system, or formal nomenclatural authority. It is an educational and research-oriented codebase for exploring how AI systems can preserve classification context, uncertainty, source traceability, and lexicon evolution.

## What Synthia Is Now

At the moment, Synthia is a local Python research core and documentation boundary for building an evolving classification intelligence. She is not yet a large model, autonomous agent, field robot, or production platform. Her current value is architectural: she provides the first working skeleton for a system that can remember which lexicon it is using, why a term belongs to that lexicon, what evidence supports it, and where uncertainty or contradiction enters the classification.

In practical terms, Synthia currently provides six base capabilities:

- represents concepts as `I_lexicon` nodes with domain, definition, source IDs, T/I/F values, and the preserved `I -> I_system^S -> H_lex -> G_lex -> I_lexicon` lexicon-classification hierarchy;
- connects concepts through typed bridges such as redescription, memory repair, analogy, contradiction, rank shift, synonymy, and uncertainty;
- produces plithogenic profiles that summarize truth, indeterminacy, falsity, contradiction load, and feature vectors for classification state;
- indexes the public NSS article list as a living source-discovery surface, then derives `P(L_i | d, S)`, `H_lex`, `G_lex`, and `I_lexicon` for math-lexicon routing;
- implements the first biology/taxonomy memory layer inspired by the white paper with Prof. Aguilar, including redescription traces, review packets, citation auditing, conservation links, and AI-assistance disclosure boundaries;
- implements the first passive swarm field-scout layer for simulated drone observations, local vision detections, digital pheromone mapping, contextual trust, anti-entropy state reconciliation, and human-review packets.

This means Synthia is currently best understood as a learning memory architecture for classification work. She does not merely store words. She stores the relation between a word, its domain, its source, its repair history, and the unresolved layers that must stay visible when the same word moves between biology, PhyloCode, AI governance, physics, or mathematical lexicons.

Her present intelligence is therefore not measured by conversation fluency. It is measured by whether she can keep taxonomic context intact while switching lexicons. The base build starts with a small seeded knowledge structure, but the intended growth pattern is clear: each new taxonomy should become a structured lexicon module, each lexicon module should add nodes and bridges, and each bridge should preserve enough evidence for a human expert or future model to understand why the classification changed.

## Core Idea

Synthia is designed to evolve each time it learns a new taxonomy. When a new field, vocabulary, or classification system is introduced, Synthia should be able to:

- add the new lexicon without erasing the old one;
- preserve source-linked definitions, uncertainty, contradictions, and repair history;
- switch between lexicons inside one task without losing context;
- identify when two fields use similar words with different meanings;
- update its internal classification graph as new evidence arrives;
- keep the hierarchy `I -> I_system^S -> H_lex -> G_lex -> I_lexicon` visible instead of flattening all uncertainty into a generic label.

## Base Build

The current base build implements:

- `I_lexicon` nodes, bridges, and context switch traces.
- Bounded T/I/F and plithogenic contradiction profiles.
- Taxonomic memory records for species names as memory objects.
- Redescription trace metadata beside formal nomenclatural authority.
- Memory repair classification, indeterminacy source location, review packets, citation auditing, conservation linking, multilingual bridges, and AI assistance disclosure tracking.
- Codex connector boundary using native Codex auth/session status, without storing OpenAI API keys in Synthia.

## Biology and PhyloCode Direction

Synthia’s first applied domain is biology, especially taxonomy, redescription, species-as-systems thinking, and PhyloCode-aware classification support.

The goal is to help organize biological knowledge as living memory:

- species names as memory objects, not only labels;
- original descriptions, redescriptions, synonymy, field notes, ecology, geography, and conservation context linked together;
- redescription treated as possible taxonomic memory repair;
- formal authorship preserved while redescriptive authority and diagnostic repair remain visible;
- PhyloCode and nomenclature concepts handled carefully without claiming to replace human taxonomists or formal Codes.

## Physics and Mathematical Classification

Synthia is also intended to support physics and mathematical classification work by preserving the vocabulary of a system, not only its surface terms. Future work will explore how physics, FfeD-style structures, plithogenic logic, and other mathematical classification systems can be mapped as separate lexicons without collapsing their specialized meanings.

## I_lexicon Indeterminacy Engine

Synthia now uses the following lexicon-classification hierarchy:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

This layer keeps lexicon indeterminacy distinct from generic uncertainty. `I` is the base indeterminacy signal. `I_system^S` is the system-level form used when a lexicon, agent state, corpus, or multi-attribute classification system organizes uncertainty. `H_lex` is normalized lexicon entropy: it measures how much a term, document, or observation is distributed across possible lexicons. `G_lex` is lexicon decision-gap uncertainty: it measures how weak the winning lexicon is against the second-best lexicon. `I_lexicon` is the final context-preserving lexicon indeterminacy state used for classification, filtration, switching, or quarantine.

Plithogenic classification is now treated as `I_system^S`, with `I_s` and `I_s_system` accepted as aliases. The public repo encodes only safe NSS source pointers and sanitized evidence metadata. Private Gmail-derived doctrine remains in `Synthia_organisation`.

The mathematical base is:

```text
P(L_i | d, S) = softmax(score(L_i, d))

H_lex = - sum(P(L_i) log(P(L_i))) / log(|L|)

G_lex = 1 - (P_top - P_second)

I_lexicon = bounded(alpha H_lex + beta G_lex + gamma contradiction_load)
```

Here `L_i` is a candidate lexicon, `d` is the document, term, or observation being classified, and `S` is the active system context. The score may combine lexical relevance, semantic similarity, taxonomy coherence, mutual-information feature dependency, source reliability, and plithogenic contradiction degree.

The symbolic engine supports stable code IDs, LaTeX forms, display forms, and algorithm forms. This gives Synthia a first practical language for lexicon entropy, lexicon decision margin, plithogenic contradiction degree, T/I/F, and source-linked document filtration without turning the project into a full symbolic algebra system yet.

The source `https://fs.unm.edu/eBook-Neutrosophics6.pdf` is treated as Synthia's primary public foundation for neutrosophic logic, set, probability, statistics, and `T/I/F`. Synthia preserves formal neutrosophic values as metadata, then converts them into bounded operational `TIF` values for deterministic software scoring.

The second NSS surface, `https://fs.unm.edu/NSS/Articles.htm`, is now treated as a living article index for source discovery. Synthia can parse article PDF links, normalize public URLs, classify titles into mathematical families, and write generated article ledgers to `Synthia_organisation` instead of the public repo. These classifications are candidate routing signals for review, not final mathematical authority.

## Future LLM Protection Layer

One future role for Synthia is to protect large language models by helping them maintain the lexicon taxonomy of the data they are responsible for. In that direction, Synthia would act as a lexicon sentinel:

- tracking which domain vocabulary an LLM is using;
- detecting when terms drift between incompatible taxonomies;
- preserving source-linked meanings and unresolved layers;
- warning when an LLM flattens specialized language into generic prose;
- helping large models stay aligned with the classification logic of the datasets they handle.

## Future Swarm and Field Discovery Vision

Long-term research may explore a swarm architecture inspired by ant pheromone communication and a queen-bee coordination model. This is future vision, not current capability.

The idea is to investigate whether Synthia-style lexicon memory could guide a swarm of drones or field agents for biodiversity exploration, including rainforest survey workflows. In a future research path, such a system could help:

- coordinate pheromone-like communication between swarm agents;
- map unexplored regions such as parts of the Amazon forest;
- collect field observations for plants, animals, habitats, and ecological signals;
- propose source-linked classification packets for new or poorly documented organisms;
- prepare PhyloCode-aware or nomenclature-aware review material for qualified human experts.

Any real-world biodiversity, drone, or field deployment would require legal authorization, ecological review, safety controls, local collaboration, and expert scientific validation.

## Boundary

Synthia can organize source-linked evidence and prepare human review packets. It does not replace taxonomists, redescriptors, museum workers, field biologists, journal editors, the ICZN, PhyloCode governance, conservation authorities, or any formal scientific authority.

The invariant below must remain visible in public payloads:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Swarm Field Scout Base

Synthia now includes a simulation-first swarm module. This is not an autonomous drone-control system. It is a passive perception and review architecture for future field work.

The current swarm layer can:

- ingest camera-frame evidence and MAVLink-like telemetry from simulated or companion-computer sources;
- normalize local CodeProject.AI-style detections into Synthia observation packets;
- classify field detections into biology, PhyloCode-adjacent taxonomy, physics signals, archaeology candidates, or general uncertainty;
- build digital pheromone cells for coverage, novelty, risk, revisit pressure, and avoid-until-review hints;
- score contextual trust with a CTN-style layer using floating location continuity, identity envelope presence, risk load, and detection quality;
- reconcile distributed node state through an anti-entropy trust ledger so stale swarm state cannot overwrite newer trust state;
- store private field evidence in `Synthia_organisation` or an optional RethinkDB backend;
- create review packets that preserve sensitive-location policy and candidate-only language.

The FfeD identity envelope is intentionally a placeholder boundary, not custom cryptography. Before any real security deployment, it must be replaced or backed by audited cryptographic primitives and formal threat modeling.

The queen coordinator currently emits task hints only. It does not command flight, change missions, override a pilot, or authorize autonomous action.

Optional RethinkDB support can be enabled for local swarm state, heartbeats, observations, and anti-entropy experiments:

```powershell
python -m pip install -e .[rethinkdb]
$env:SYNTHIA_RETHINKDB_HOST="127.0.0.1"
$env:SYNTHIA_RETHINKDB_PORT="28015"
$env:SYNTHIA_RETHINKDB_DB="synthia_swarm"
python -m synthia_core.cli swarm backend status
python -m synthia_core.cli swarm backend ensure-schema
```

This gives Synthia a real backend memory surface for swarm work. With RethinkDB available, Synthia can move beyond one-shot CLI packets and begin keeping a live operational history of field agents:

- drone or simulator nodes can publish heartbeats into a shared trust surface;
- observations can persist as queryable records instead of disappearing after one command;
- CTN trust state can be reconciled across nodes instead of being held only in local process memory;
- anti-entropy repair can reject stale swarm state and preserve newer node knowledge;
- disconnected nodes can buffer observations, replay them later, and still deduplicate by observation identity;
- queen coordination can reason over remembered coverage, novelty, risk, and review state;
- future dashboards or APIs can subscribe to state changes instead of polling flat files;
- private media and sensitive coordinates can remain in `Synthia_organisation` while public packets expose only safe summaries.

In Synthia’s architecture, RethinkDB is not just storage. It is the first practical substrate for CTN-style swarm memory: a place where field observations, trust transitions, pheromone-map updates, and human-review boundaries can stay synchronized while the lexicon layer keeps the classification context intact.

## HippoRAG Memory Trace Bridge

Synthia now includes an optional HippoRAG-style memory trace layer for RethinkDB. It does not vendor or replace HippoRAG. Instead, it gives Synthia a compatible graph-memory surface where RAG memory bits can be traced by lexicon type, graph location, selection mechanism, and plithogenic state.

This gives Synthia a way to keep track of where a knowledge fragment lives inside a RAG graph:

- `lexicon_type`: biology, taxonomy, PhyloCode, physics, archaeology, conservation, AI governance, FfeD/math, or another domain;
- `memory_bit_id`: stable identifier for the remembered unit;
- `graph_location`: namespace, node type, node id, chunk id, entity id, fact id, edge id, and hop depth;
- `selection_mechanism`: dense passage retrieval, fact reranking, personalized PageRank, lexicon bridge, plithogenic trace, or manual review;
- `tif`: full `T/I/F` plus the lexicon indeterminacy state `I_system^S`, `H_lex`, `G_lex`, and `I_lexicon` when available;
- `plithogenic_profile`: a bounded trace of contradiction, weighted truth, and feature-vector state.

The intended role is to let Synthia remember not only what a retrieved passage says, but why it was selected, which lexicon it belongs to, where it sits in the graph, and what uncertainty structure came with it. This is the bridge between Synthia’s `I_lexicon` and HippoRAG-style long-term associative memory.

RethinkDB tables used by this bridge:

- `hipporag_memory_bits`
- `hipporag_graph_edges`
- `hipporag_selection_traces`

Example:

```powershell
python -m synthia_core.cli hipporag backend ensure-schema
python -m synthia_core.cli hipporag trace add --lexicon-type taxonomy --node-id fact-aburria-redescription --content "Aburria aburri redescription repairs diagnostic context." --selection-mechanism fact_rerank --relevance 0.91 --T 0.86 --I 0.12 --F 0.02 --source-id hipporag-case-study
python -m synthia_core.cli hipporag trace select --lexicon-type taxonomy --selection-mechanism fact_rerank
```

## CLI

Run from the repository root:

```powershell
python -m synthia_core.cli sources scan-root
python -m synthia_core.cli soul build --private-org ..\Synthia_organisation
python -m synthia_core.cli lexicon classify --text "AI-assisted traceability supports human review." --domain ai_governance
python -m synthia_core.cli lexicon switch --from taxonomy --to phylocode_nomenclature --context ctx-1
python -m synthia_core.cli lexicon i-chain explain --term "plithogenic contradiction"
python -m synthia_core.cli lexicon i-chain classify --text "lexicon entropy and weak decision gap in taxonomy memory" --domain ffed_math
python -m synthia_core.cli lexicon notation render --symbol I_s --format latex
python -m synthia_core.cli nss sources list
python -m synthia_core.cli nss route --text "plithogenic contradiction degree"
python -m synthia_core.cli nss foundation explain
python -m synthia_core.cli nss foundation normalize --T 1.2 --I 0.4 --F -0.1 --profile standard
python -m synthia_core.cli nss foundation profile --name paradoxist
python -m synthia_core.cli nss articles scan --limit 25 --private-org ..\Synthia_organisation
python -m synthia_core.cli nss articles classify --text "neutrosophic probability distribution for lexicon entropy"
python -m synthia_core.cli nss articles source --url https://fs.unm.edu/NSS/PlithogenicSetAnExtensionOfCrisp.pdf
python -m synthia_core.cli nss index explain --text "hypersoft multi-criteria taxonomy filtering"
python -m synthia_core.cli plithogenic profile --source nss.plithogenic_logic
python -m synthia_core.cli taxonomy aburria-packet
python -m synthia_core.cli swarm queen status
python -m synthia_core.cli swarm node run --config .\node_config.json
python -m synthia_core.cli swarm ingest-frame --image .\sample_tree.jpg --telemetry "{`"latitude`":1.1,`"longitude`":2.2}" --detection tree:0.74
python -m synthia_core.cli swarm ingest-frame --image .\sample_tree.jpg --telemetry "{`"latitude`":1.1,`"longitude`":2.2}" --detection tree:0.74 --store
python -m synthia_core.cli swarm review-packet build --detection frog:0.81
python -m synthia_core.cli swarm review-packet build --observation obs.example --private-org ..\Synthia_organisation
python -m synthia_core.cli swarm safety-check --mission "{`"simulation_passed`":false}"
python -m synthia_core.cli codex status
python -m synthia_core.cli codex wake-prompt --private-org ..\Synthia_organisation
```

## Development

```powershell
python -m pytest
```

No raw private emails, authentication caches, unpublished article bodies, or token material should be committed to this repository.
