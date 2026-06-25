# Plithogenic Set Kernel

## Objective

This document records Synthia phase 14. The plithogenic set kernel models attribute values, dominant values, and contradiction degree as a system-level input to:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Source

- Phase 14 source: [Plithogenic Set, an Extension of Crisp, Fuzzy, Intuitionistic Fuzzy, and Neutrosophic Sets](https://fs.unm.edu/NSS/PlithogenicSetAnExtensionOfCrisp.pdf)

## Synthia Role

The kernel is implemented in `synthia_core.plithogenic_set`. It supports attribute-spectrum scoring, dominant attribute selection, contradiction load, and bounded union, intersection, and complement diagnostics.

## Public CLI

```text
synthia plithogenic set explain
synthia plithogenic set score --attributes <json>
synthia plithogenic set operate --op union|intersection|complement --left <json> --right <json>
```

## Boundary

Plithogenic set output is classified as system-level `I_system^S`. It feeds contradiction load into Synthia's lexicon chain but does not replace that chain.
