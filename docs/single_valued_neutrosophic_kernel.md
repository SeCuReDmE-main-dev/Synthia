# Single-Valued Neutrosophic Kernel

## Objective

This document records Synthia phase 7. The single-valued neutrosophic kernel gives Synthia bounded set operations for current runtime scoring while preserving the public hierarchy:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Source

- Phase 7 source: [Single Valued Neutrosophic Sets](https://fs.unm.edu/SingleValuedNeutrosophicSets.pdf)

## Synthia Role

The kernel is implemented in `synthia_core.single_valued_neutrosophic`. It supports bounded union, intersection, difference, truth-favorite, and falsity-favorite operations.

Synthia uses these operators for practical computation over operational `TIF` values. Formal neutrosophic richness remains represented in the foundation layer.

## Public CLI

```text
synthia nss svns explain
synthia nss svns operate --op union|intersection|difference --left <T,I,F> --right <T,I,F>
synthia nss svns favorite --mode truth|falsity --T <value> --I <value> --F <value>
```

## Boundary

These operations are bounded software operators for Synthia's current classifier. They are not a replacement for expert mathematical review.
