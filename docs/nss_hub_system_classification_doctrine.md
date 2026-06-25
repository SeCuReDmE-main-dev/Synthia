# NSS Hub as Synthia's System-Classification Entrydoor

## Objective

This document defines how Synthia uses the public NSS hub as the entrydoor for mathematical source families while preserving the corrected `I_lexicon` classification chain.

Primary public entrydoor:

```text
https://fs.unm.edu/NSS/
```

## Core Doctrine

Synthia does not treat the NSS hub as one formula. It treats it as a public mathematical map of source families: neutrosophy, T/I/F, probability and statistics, plithogenic methods, symbolic algebra, hypersoft structures, NeutroAlgebra, NeutroGeometry, topology, and future mathematical lexicons.

The first rule is system-location:

```text
I -> I_system^S
```

This means that indeterminacy must be placed inside an active system before Synthia chooses a carrier. The active system may be a lexicon, corpus, task, source family, graph trace, taxonomy packet, or specialized mathematical domain.

The default public carrier for Synthia is the lexicon-classification carrier:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

`H_lex` measures lexicon entropy. `G_lex` measures decision-gap uncertainty between the strongest and second-strongest candidate lexicons. `I_lexicon` is the final context-preserving state used for classification, filtration, switching, or quarantine.

## Specialized Carriers

Specialized mathematical domains may define their own carrier variables after `I_system^S`, but they do not replace the public default chain.

For example, a geometric or multiscale branch may use a specialized carrier profile. That profile is only emitted when Synthia explicitly routes into `fractal_geometry` or `neutrogeometry`. It is not returned by default text classification, taxonomy memory, HippoRAG trace, or swarm review packets.

## Plithogenic Role

Plithogenic mathematics is a system-level multi-attribute contradiction layer. It helps Synthia aggregate:

- attributes;
- attribute values;
- dominant values;
- contradiction degree;
- T/I/F state;
- source-weighted evidence.

Plithogenic output supports `I_system^S` and helps compute contradiction load before the final lexicon carrier is selected.

## Implementation Mapping

- `NSSMathRouter`: detects the NSS source family and selects the correct carrier.
- `SystemIndeterminacyChain`: stores the generic public chain.
- `FractalCarrierProfile`: stores specialized geometric/multiscale carrier data only when explicitly requested.
- `PlithogenicMatrix`: computes contradiction and weighted T/I/F before `H_lex`, `G_lex`, and `I_lexicon` are finalized.
- `HippoRAGMemoryBit`: stores graph memory with lexicon type, graph location, source IDs, T/I/F, and the public system-indeterminacy chain.

## Public Boundary

This doctrine document cites public NSS sources only. Internal book-derived reasoning informs the architecture, but raw local notes, private correspondence, and restricted evidence are not part of the public repo.
