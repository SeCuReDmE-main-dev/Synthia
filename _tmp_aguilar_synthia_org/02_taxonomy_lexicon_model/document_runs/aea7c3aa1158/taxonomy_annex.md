# Synthia Taxonomy Review Annex

## Run Metadata
- Run ID: `aea7c3aa1158`
- Profile: `taxonomy-review`
- Input path: `C:\Users\jeans\Desktop\Case study\modele\Synthia\Synthia\tests\fixtures\document_pipeline_taxonomy_review.md`
- Input format: `md`
- Block count: `5`

## Boundary
- Synthia performs ingestion, classification, lexicon extraction, and annex generation only; it does not translate, style-polish, export DOCX, or claim autonomous authority.
- Formal nomenclatural authority remains governed by the relevant Code and human review.
- Human review required: `true`

## Ownership
- Synthia-owned stages: `ingest`, `classify`, `lexicon`, `annex`, `handoff`
- Codex-owned downstream work begins only after this handoff bundle exists.

## Source IDs
- Public seed source IDs remain visible through lexicon summary artifacts.
- Profile source ID: `document.profile.taxonomy-review`

## Coverage
- `taxonomy`: `2` block(s)
- `phylocode_nomenclature`: `1` block(s)
- `conservation`: `1` block(s)
- `ai_governance`: `1` block(s)
- `general`: `0` block(s)
- Unresolved blocks: `1`

## Domain: taxonomy
- `blk-0001` matched `species as systems`; unresolved=`false`
- `blk-0002` matched `species as systems, taxonomy`; unresolved=`false`

## Domain: phylocode_nomenclature
- `blk-0003` matched `taxonomic, clade, nomenclature, phylocode, redescription, taxonomic memory repair`; unresolved=`true`

## Domain: conservation
- `blk-0004` matched `conservation, conservation report, habitat monitoring, integral conservation`; unresolved=`false`

## Domain: ai_governance
- `blk-0005` matched `AI-assisted traceability, human review, review boundary, source-linked evidence, traceability`; unresolved=`false`

## Unresolved Blocks
- `blk-0003` dominant=`phylocode_nomenclature` candidate_terms=`taxonomic, memory, repair, phylocode, nomenclature`

Hierarchy: `I -> I_system^S -> H_lex -> G_lex -> I_lexicon`
