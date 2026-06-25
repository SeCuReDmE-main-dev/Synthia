# Plithogenic Logic Kernel

## Objective

This document records Synthia phase 15. The plithogenic logic kernel models many-variable proposition truth and cumulative truth under the public hierarchy:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Source

- Phase 15 source: [Introduction to Plithogenic Logic](https://fs.unm.edu/NSS/IntroductionPlithogenicLogic1.pdf)

## Synthia Role

The kernel is implemented in `synthia_core.plithogenic_logic`. It supports many-variable truth values, dependence metadata, cumulative truth, and category routing for Boolean, fuzzy, neutrosophic, indeterminate, and general plithogenic logic.

## Public CLI

```text
synthia plithogenic logic explain
synthia plithogenic logic classify --variables <json>
```

## Boundary

Plithogenic logic remains an `I_system^S` method for multi-variable system indeterminacy. It supports Synthia's lexicon classification but does not create a separate public chain.
