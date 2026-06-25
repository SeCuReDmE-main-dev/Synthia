# Plithogenic Probability And Statistics Kernel

## Objective

This kernel implements Synthia phase 16 from the public NSS source:

https://fs.unm.edu/NSS/PlithogenicProbabilityStatistics20.pdf

It treats plithogenic probability as a multi-variable probability and statistics layer where each variable can preserve truth, indeterminacy, falsity, weight, distribution metadata, and contradiction load.

## Synthia Role

The kernel feeds the public hierarchy:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

Plithogenic probability remains a system-level method. It does not replace `I_lexicon`; it supplies contradiction and refined component evidence used by `I_system^S`, `H_lex`, `G_lex`, and `I_lexicon`.

## Public Interfaces

```text
synthia plithogenic probability explain
synthia plithogenic probability event --variables <json>
synthia plithogenic probability refine --components <json>
```

## Implementation Boundary

The v1 implementation is deterministic and bounded. Formal values are preserved in source-facing records, while operational scoring clamps values for software use.
