# Neutrosophic Foundation Kernel

## Objective

Synthia uses the public source https://fs.unm.edu/eBook-Neutrosophics6.pdf as the primary foundation reference for neutrosophic truth, indeterminacy, falsity, logic, set, probability, and statistics.

This source supports the base `T/I/F` layer beneath Synthia's public classification chain:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Formal and Operational Values

The foundation layer separates formal neutrosophic values from Synthia's operational runtime values.

Formal values preserve the submitted `T`, `I`, and `F` values and their profile context. Operational values are bounded to `0..1` so Synthia can use them safely in deterministic scoring, graph traces, review packets, swarm packets, and `I_lexicon` calculations.

This means Synthia can record formal richness while still producing stable payloads for software use.

## Profiles

The first implementation includes deterministic profiles:

- `standard`: ordinary bounded operational `T/I/F`.
- `paradoxist`: high truth and high falsity can coexist.
- `dialetheist`: contradiction-bearing set or proposition profile.
- `tautological`: absolute or near-absolute truth profile.
- `nihilist`: near-empty or denial-heavy profile.
- `uncertain`: indeterminacy-dominant profile.

These profiles are public-safe mathematical categories for routing and review. They are not claims of final authority about a specific article, theorem, or scientific result.

## Relationship To I_lexicon

`T/I/F` is the foundation layer. `I_system^S` locates indeterminacy inside a system. `H_lex`, `G_lex`, and `I_lexicon` are Synthia engineering variables built above that foundation for lexicon classification, document filtration, switching, and quarantine.

Fractal or geometric carriers remain specialized branches and are not the default public chain.
