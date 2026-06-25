# Neutrosophic Random Variables Kernel

## Objective

This document records Synthia phase 11. The random-variable kernel models a neutrosophic random variable as a bounded software object while preserving the public hierarchy:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Public Source

- Phase 11 source: [Neutrosophic Random Variables](https://fs.unm.edu/NSS/NeutrosophicRandomVariables4.pdf)

## Synthia Role

The kernel is implemented in `synthia_core.neutrosophic_random_variables`. It supports random-variable definition, symbolic PDF/PMF/CDF metadata, expected value, variance, standard deviation, moment summaries, and `I_lexicon` projection.

## Public CLI

```text
synthia nss random-variable explain
synthia nss random-variable define --name <name> --base <value> --I <value>
synthia nss random-variable summarize --values <json>
```

## Boundary

Synthia stores symbolic distribution metadata for routing and review. It does not perform full symbolic calculus in this kernel.
