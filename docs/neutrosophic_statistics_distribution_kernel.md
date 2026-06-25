# Neutrosophic Statistics And Distribution Kernel

## Objective

This document records Synthia phases 9 and 10. The statistics and distribution kernel summarizes known, interval, and unknown data while preserving Synthia's lexicon hierarchy:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Sources

- Phase 9 source: [Introduction to Neutrosophic Statistics](https://fs.unm.edu/NeutrosophicStatistics.pdf)
- Phase 10 source: [The Neutrosophic Statistical Distribution](https://fs.unm.edu/NSS/TheNeutrosophicStatisticalDistribution.pdf)

## Synthia Role

The kernel is implemented in `synthia_core.neutrosophic_statistics`. It produces deterministic descriptive summaries:

- known count;
- unknown count;
- interval count;
- indeterminacy load;
- range and representative mean when available;
- candidate distribution labels;
- review risk.

## Public CLI

```text
synthia nss statistics explain
synthia nss statistics summarize --values <json>
synthia nss distribution classify --text <text>
```

## Boundary

The distribution classifier emits candidate labels for routing and review. It does not make final statistical or scientific claims.
