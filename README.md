# Synthia

Synthia is an educational research project for an evolving `I_lexicon`: a context-preserving lexicon and taxonomy core that updates as it learns new classification systems.

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

In practical terms, Synthia currently does four things:

- represents concepts as `I_lexicon` nodes with domain, definition, source IDs, T/I/F values, and the preserved `I -> I_system^S -> D_f -> dF -> i_fractal` hierarchy;
- connects concepts through typed bridges such as redescription, memory repair, analogy, contradiction, rank shift, synonymy, and uncertainty;
- produces plithogenic profiles that summarize truth, indeterminacy, falsity, contradiction load, and feature vectors for classification state;
- implements the first biology/taxonomy memory layer inspired by the white paper with Prof. Aguilar, including redescription traces, review packets, citation auditing, conservation links, and AI-assistance disclosure boundaries.

This means Synthia is currently best understood as a learning memory architecture for classification work. She does not merely store words. She stores the relation between a word, its domain, its source, its repair history, and the unresolved layers that must stay visible when the same word moves between biology, PhyloCode, AI governance, physics, or mathematical lexicons.

Her present intelligence is therefore not measured by conversation fluency. It is measured by whether she can keep taxonomic context intact while switching lexicons. The base build starts with a small seeded knowledge structure, but the intended growth pattern is clear: each new taxonomy should become a structured lexicon module, each lexicon module should add nodes and bridges, and each bridge should preserve enough evidence for a human expert or future model to understand why the classification changed.

## Core Idea

Synthia is designed to evolve each time it learns a new taxonomy. When a new field, vocabulary, or classification system is introduced, Synthia should be able to:

- add the new lexicon without erasing the old one;
- preserve source-linked definitions, uncertainty, contradictions, and repair history;
- switch between lexicons inside one task without losing context;
- identify when two fields use similar words with different meanings;
- update its internal classification graph as new evidence arrives;
- keep the hierarchy `I -> I_system^S -> D_f -> dF -> i_fractal` visible instead of flattening all uncertainty into a generic label.

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

Synthia is also intended to support physics and mathematical classification work by preserving the vocabulary of a system, not only its surface terms. Future work will explore how lexicons from Fractal NeutroGeometry, FfeD-style structures, plithogenic logic, and related classification systems can be mapped without collapsing their specialized meanings.

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
I -> I_system^S -> D_f -> dF -> i_fractal
```

## CLI

Run from the repository root:

```powershell
python -m synthia_core.cli sources scan-root
python -m synthia_core.cli soul build --private-org ..\Synthia_organisation
python -m synthia_core.cli lexicon classify --text "AI-assisted traceability supports human review." --domain ai_governance
python -m synthia_core.cli lexicon switch --from taxonomy --to phylocode_nomenclature --context ctx-1
python -m synthia_core.cli taxonomy aburria-packet
python -m synthia_core.cli codex status
python -m synthia_core.cli codex wake-prompt --private-org ..\Synthia_organisation
```

## Development

```powershell
python -m pytest
```

No raw private emails, authentication caches, unpublished article bodies, or token material should be committed to this repository.
