# Independent Neutrosophic Components Kernel

## Objective

This document records Synthia phase 12. The component kernel preserves independent, partially dependent, dependent, and offset T/I/F components before they are bounded for runtime use:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Source

- Phase 12 source: [Practical Applications of the Independent Neutrosophic Components and of the Neutrosophic Offset Components](https://fs.unm.edu/NSS/PracticalIndependentNeutrosophic36.pdf)

## Synthia Role

The kernel is implemented in `synthia_core.independent_neutrosophic_components`. It preserves formal component values, records dependency mode, detects offset components outside the bounded runtime interval, and produces an operational `TIF` projection.

## Public CLI

```text
synthia nss components explain
synthia nss components classify --T <value> --I <value> --F <value> --mode independent|partial|dependent|offset
```

## Boundary

Formal component values are preserved as evidence. Synthia's scoring layer remains bounded for deterministic graph, review, and lexicon outputs.
