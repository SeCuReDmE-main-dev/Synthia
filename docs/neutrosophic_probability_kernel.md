# Neutrosophic Probability Kernel

## Objective

This document records Synthia phase 8. The probability kernel models event triples, complement behavior, and sample-space diagnostics before probability evidence is projected into:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Source

- Phase 8 source: [Introduction to Neutrosophic Measure, Integral, and Probability](https://fs.unm.edu/NeutrosophicMeasureIntegralProbability.pdf)

## Synthia Role

The kernel is implemented in `synthia_core.neutrosophic_probability`. It supports:

- event triples with `T`, `I`, and `F`;
- empty event representation;
- complement summaries;
- sample-space checks;
- probability-to-`I_lexicon` conversion.

## Public CLI

```text
synthia nss probability explain
synthia nss probability event --name <name> --T <value> --I <value> --F <value>
synthia nss probability sample-space --events <json>
```

## Boundary

Synthia treats probability outputs as reviewable classification evidence. The public repo stores only source IDs, URLs, and sanitized summaries.
