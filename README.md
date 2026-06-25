# Synthia

Synthia is an `I_lexicon` research core for context-preserving lexicon switching, taxonomic memory repair, and responsible AI-assisted traceability.

Author identifier: Jean-Sebastien Beaulieu, ORCID: https://orcid.org/0009-0007-2904-0443

The public repository contains code, tests, and safe public documentation only. Private source ledgers, Gmail-derived evidence summaries, implementation notes, and the full soul draft live beside this repo in:

```text
..\Synthia_organisation
```

## Base Build

The current base build implements:

- `I_lexicon` nodes, bridges, and context switch traces.
- Bounded T/I/F and plithogenic contradiction profiles.
- Taxonomic memory records for species names as memory objects.
- Redescription trace metadata beside formal nomenclatural authority.
- Memory repair classification, indeterminacy source location, review packets, citation auditing, conservation linking, multilingual bridges, and AI assistance disclosure tracking.
- Codex connector boundary using native Codex auth/session status, without storing OpenAI API keys in Synthia.

## Boundary

Synthia can organize source-linked evidence and prepare human review packets. It does not replace taxonomists, redescriptors, museum workers, field biologists, journal editors, the ICZN, or any formal nomenclatural authority.

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
