# MultiNeutrosophic Kernel

## Objective

This document records Synthia phase 13. The MultiNeutrosophic kernel fuses many source assessments while preserving the public lexicon chain:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Source

- Phase 13 source: [Introduction to the MultiNeutrosophic Set](https://fs.unm.edu/NSS/MultiNeutrosophicSet.pdf)

## Synthia Role

The kernel is implemented in `synthia_core.multineutrosophic`. It supports source-weighted T/I/F assessments, fusion, agreement scoring, conflict scoring, review risk, and bounded `I_lexicon` projection.

## Public CLI

```text
synthia nss multi-set explain
synthia nss multi-set fuse --assessments <json>
```

## Boundary

Multi-source fusion is a candidate review signal. Synthia does not treat source agreement as final authority.
