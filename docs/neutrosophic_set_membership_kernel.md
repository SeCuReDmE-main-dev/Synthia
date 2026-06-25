# Neutrosophic Set Membership Kernel

## Objective

Synthia uses https://fs.unm.edu/IFS-generalized.pdf as the public source for interpreting neutrosophic set membership and its relationship to intuitionistic fuzzy sets.

The default Synthia chain remains:

```text
I -> I_system^S -> H_lex -> G_lex -> I_lexicon
```

## Membership Interpretation

The set-membership kernel interprets a formal `T/I/F` tuple as:

- `T`: membership or truth-membership;
- `I`: indeterminacy of membership;
- `F`: non-membership or falsity-membership.

The formal tuple is preserved. Synthia then derives bounded operational `TIF` values for deterministic scoring, review packets, graph traces, swarm packets, and `I_lexicon` calculations.

## Classification Labels

The first implementation classifies tuples as `consistent_complete`, `incomplete`, `paraconsistent`, `intuitionistic_fuzzy_compatible`, over/under component states, and `general_neutrosophic`.

IFS compatibility is a diagnostic boundary. It does not replace neutrosophic set membership. A tuple can be useful to Synthia even when it is not intuitionistic-fuzzy-compatible.

## Boundary

This layer adds set interpretation. It does not redesign article indexing, plithogenic scoring, HippoRAG traces, swarm state, or taxonomy memory. Fractal and geometric carriers remain specialized branches and are not emitted by default.
